import random
import networkx as nx
import json
from deap import base, creator, tools, algorithms
from evaluate import evaluate, DEATH_PENALTY, _prereq_satisfied
from create_graph import load_data_from_json, create_graph


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

def _semester_can_take(
    course_id,
    sem_hours,
    total_hours,
    max_hours,
    max_total_hours,
    remaining_semesters_after_current,
    min_utd_per_sem,
    G,
):
    course_hours = G.nodes[course_id].get("credit_hours", 0)
    if sem_hours + course_hours > max_hours:
        return False
    if total_hours + sem_hours + course_hours > max_total_hours:
        return False
    if min_utd_per_sem is not None and min_utd_per_sem > 0:
        reserved_future_hours = remaining_semesters_after_current * min_utd_per_sem
        if total_hours + sem_hours + course_hours + reserved_future_hours > max_total_hours:
            return False
    return True


def _choose_location(course_id, sem_utd_hours, min_utd_per_sem, G):
    is_transferable = G.nodes[course_id].get("is_transferable", False)
    if not is_transferable:
        return "U"
    if min_utd_per_sem is not None and sem_utd_hours < min_utd_per_sem:
        return "U"
    if min_utd_per_sem is not None and min_utd_per_sem > 0:
        return "C"
    return random.choice(["U", "C"])


def _is_utd_location(location):
    return location == "U"


def _has_unmet_requirements(core_hours_collected, requirements):
    if not requirements:
        return False
    for core_cat, info in requirements.items():
        if not isinstance(info, dict) or core_cat == "mandatory_exact_matches":
            continue
        if core_hours_collected.get(core_cat, 0) < info.get("hours_required", 0):
            return True
    return False


def _contributes_to_unmet_requirement(course_id, core_hours_collected, requirements):
    if not requirements:
        return False
    for core_cat, info in requirements.items():
        if not isinstance(info, dict) or core_cat == "mandatory_exact_matches":
            continue
        if core_hours_collected.get(core_cat, 0) >= info.get("hours_required", 0):
            continue
        if course_id in info.get("courses", []):
            return True
    return False


def _core_requirement_categories(requirements):
    if not requirements:
        return []
    return [
        category
        for category, info in requirements.items()
        if isinstance(info, dict) and category.startswith("core_")
    ]


def _is_core_course(course_id, requirements):
    for category in _core_requirement_categories(requirements):
        if course_id in requirements[category].get("courses", []):
            return True
    return False


def _semester_hours(semester, G):
    return sum(G.nodes[course.split('_')[0]].get("credit_hours", 0) for course in semester)


def _semester_utd_hours(semester, G):
    return sum(
        G.nodes[course.split('_')[0]].get("credit_hours", 0)
        for course in semester
        if course.split('_')[1] == "U"
    )


def _semester_is_all_core(semester, requirements):
    if not semester:
        return False
    return all(_is_core_course(course.split('_')[0], requirements) for course in semester)


def _can_move_semester_courses(courses, target_semester, target_idx, individual, G, max_hours):
    target_term = "Fall" if target_idx % 2 == 0 else "Spring"
    if _semester_hours(target_semester, G) + _semester_hours(courses, G) > max_hours:
        return False

    history_before_target = set()
    for semester in individual[:target_idx]:
        history_before_target.update(course.split('_')[0] for course in semester)

    for course in courses:
        base_id = course.split('_')[0]
        data = G.nodes[base_id]
        if target_term not in data.get("availability", []):
            return False
        if not all(_prereq_satisfied(prereq, base_id, history_before_target) for prereq in data.get("prereqs", [])):
            return False
    return True


def generate_individual(
    G,
    max_semesters=8,
    max_hours=19,
    preferred_max_hours=17,
    max_total_hours=125,
    requirements=None,
    seed_mode=False,
):
    individual = []
    history = set()
    remaining_nodes = set(G.nodes())
    total_hours = 0
    # Track accumulated core hours while constructing the individual so we can
    # prefer courses that fill deficits.
    core_hours_collected = {key: 0 for key in (requirements or {})}
    min_utd_per_sem = requirements.get("min_utd_hours_per_sem", None) if requirements else None
    
    for sem_idx in range(max_semesters):
        semester = []
        sem_hours = 0
        sem_utd_hours = 0
        sem_utd_course_count = 0
        term = "Fall" if sem_idx % 2 == 0 else "Spring"
        semester_max_hours = max_hours if sem_idx == max_semesters - 1 else preferred_max_hours
        remaining_semesters_after_current = max_semesters - sem_idx - 1
        
        candidates = []
        for node in remaining_nodes:
            node_data = G.nodes[node]
            node_prereqs = node_data.get("prereqs", [])
            
            prereqs_met = all(_prereq_satisfied(p, node, history) for p in node_prereqs)
            
            available_now = term in node_data.get("availability", [])
            if prereqs_met and available_now:
                candidates.append(node)
        # Prioritize candidates that help satisfy requirements:
        # - mandatory_exact_matches are highest priority
        # - courses that contribute hours to core categories with the largest deficit
        mand_list = []
        if requirements and "mandatory_exact_matches" in requirements:
            mand_list = requirements["mandatory_exact_matches"].get("courses", [])

        def score_node(node):
            score = 0
            ch = G.nodes[node].get("credit_hours", 0)
            is_transferable = G.nodes[node].get("is_transferable", False)
            is_utd = not G.nodes[node].get("is_transferable", False)
            is_core_course = _is_core_course(node, requirements)
            contributes_unmet_requirement = _contributes_to_unmet_requirement(
                node, core_hours_collected, requirements
            )
            # big boost if node is a mandatory exact-match
            if node in mand_list:
                score += 1000
            # If the semester is still below the minimum UTD target, prioritize UTD courses.
            if min_utd_per_sem is not None and sem_hours >= 0:
                if sem_utd_hours < min_utd_per_sem and is_utd:
                    score += 500
                if sem_utd_hours >= min_utd_per_sem and is_transferable:
                    score += 200
            # add score proportional to how much this node would reduce deficits
            if requirements:
                for core_cat, info in requirements.items():
                    if not isinstance(info, dict):
                        continue
                    if core_cat == "mandatory_exact_matches":
                        continue
                    needed = max(0, info.get("hours_required", 0) - core_hours_collected.get(core_cat, 0))
                    if needed <= 0:
                        continue
                    requirement_courses = info.get("courses", [])
                    if node in requirement_courses:
                        # Strongly prefer unmet audit buckets before extra electives.
                        scarcity_bonus = max(0, 100 - len(requirement_courses))
                        major_bonus = 300 if core_cat == "major_technical_electives" else 0
                        score += 200 + scarcity_bonus + major_bonus + min(ch, needed)
            # Avoid piling leftover cores into the back half of the degree.
            if sem_idx >= 5 and is_core_course and not contributes_unmet_requirement:
                score -= 500
            if sem_idx >= 6 and is_core_course and not contributes_unmet_requirement:
                score -= 1200
            if sem_idx >= 6 and not is_core_course:
                score += 250
            if len(semester) >= 3 and _semester_is_all_core(semester, requirements) and not is_core_course:
                score += 1500
            return score

        # Force schedule any available mandatory exact-match courses first.
        mand_candidates = [n for n in candidates if n in mand_list]
        mand_candidates.sort(
            key=lambda node: (
                G.nodes[node].get("is_transferable", False),
                -G.nodes[node].get("credit_hours", 0),
                node,
            )
        )
        for m in mand_candidates:
            course_hours = G.nodes[m].get("credit_hours", 0)
            if _semester_can_take(
                m,
                sem_hours,
                total_hours,
                semester_max_hours,
                max_total_hours,
                remaining_semesters_after_current,
                min_utd_per_sem,
                G,
            ):
                location = _choose_location(m, sem_utd_hours, min_utd_per_sem, G)
                semester.append(f"{m}_{location}")
                sem_hours += course_hours
                if _is_utd_location(location):
                    sem_utd_hours += course_hours
                    sem_utd_course_count += 1
                # update running core hours
                if requirements:
                    for core_cat, info in requirements.items():
                        if not isinstance(info, dict):
                            continue
                        if core_cat == "mandatory_exact_matches":
                            continue
                        if m in info.get("courses", []):
                            core_hours_collected[core_cat] += G.nodes[m].get("credit_hours", 0)
        # remove any mand candidates we scheduled from the generic candidate pool
        candidates = [c for c in candidates if c not in mand_candidates]

        # Sort remaining candidates by score descending to prefer requirement-fillers.
        # In seed mode, prefer deterministic ordering so the GA always gets a stable
        # near-feasible starting individual.
        if seed_mode:
            candidates.sort(key=lambda n: (score_node(n), n), reverse=True)
        else:
            random.shuffle(candidates)
            candidates.sort(key=lambda n: (score_node(n), n), reverse=True)
        for course_id in candidates:
            course_hours = G.nodes[course_id].get("credit_hours", 0)
            is_core_course = _is_core_course(course_id, requirements)
            all_current_courses_are_core = _semester_is_all_core(semester, requirements)
            if (
                course_id not in mand_list
                and _has_unmet_requirements(core_hours_collected, requirements)
                and not _contributes_to_unmet_requirement(course_id, core_hours_collected, requirements)
                and not (len(semester) >= 3 and all_current_courses_are_core and not is_core_course)
            ):
                continue
            if (
                sem_idx >= 6
                and is_core_course
                and not _contributes_to_unmet_requirement(course_id, core_hours_collected, requirements)
            ):
                non_core_alternative_exists = any(
                    other != course_id
                    and not _is_core_course(other, requirements)
                    and _semester_can_take(
                        other,
                        sem_hours,
                        total_hours,
                        semester_max_hours,
                        max_total_hours,
                        remaining_semesters_after_current,
                        min_utd_per_sem,
                        G,
                    )
                    for other in candidates
                )
                if non_core_alternative_exists:
                    continue
            if _semester_can_take(
                course_id,
                sem_hours,
                total_hours,
                semester_max_hours,
                max_total_hours,
                remaining_semesters_after_current,
                min_utd_per_sem,
                G,
            ):
                location = _choose_location(course_id, sem_utd_hours, min_utd_per_sem, G)
                semester.append(f"{course_id}_{location}")
                sem_hours += course_hours
                if _is_utd_location(location):
                    sem_utd_hours += course_hours
                    sem_utd_course_count += 1
                # update running core hours so next semesters prioritize unmet buckets
                if requirements:
                    for core_cat, info in requirements.items():
                        if not isinstance(info, dict):
                            continue
                        if core_cat == "mandatory_exact_matches":
                            continue
                        if course_id in info.get("courses", []):
                            core_hours_collected[core_cat] += G.nodes[course_id].get("credit_hours", 0)

        # If the semester still does not meet the UTD minimum, do a second pass
        # that aggressively tops it up with any remaining UTD-eligible courses.
        if min_utd_per_sem is not None and sem_utd_hours < min_utd_per_sem:
            utd_candidates = []
            scheduled_this_sem = {course.split('_')[0] for course in semester}
            for course_id in candidates:
                if course_id in scheduled_this_sem:
                    continue
                if G.nodes[course_id].get("is_transferable", False):
                    continue
                if _semester_can_take(
                    course_id,
                    sem_hours,
                    total_hours,
                    semester_max_hours,
                    max_total_hours,
                    remaining_semesters_after_current,
                    min_utd_per_sem,
                    G,
                ):
                    utd_candidates.append(course_id)
            if seed_mode:
                utd_candidates.sort(key=lambda n: (G.nodes[n].get("credit_hours", 0), n), reverse=True)
            else:
                random.shuffle(utd_candidates)
                utd_candidates.sort(key=lambda n: (G.nodes[n].get("credit_hours", 0), n), reverse=True)
            for course_id in utd_candidates:
                course_hours = G.nodes[course_id].get("credit_hours", 0)
                if sem_utd_hours >= min_utd_per_sem:
                    break
                if _semester_can_take(
                    course_id,
                    sem_hours,
                    total_hours,
                    semester_max_hours,
                    max_total_hours,
                    remaining_semesters_after_current,
                    min_utd_per_sem,
                    G,
                ):
                    semester.append(f"{course_id}_U")
                    scheduled_this_sem.add(course_id)
                    sem_hours += course_hours
                    sem_utd_hours += course_hours
                    if requirements:
                        for core_cat, info in requirements.items():
                            if not isinstance(info, dict):
                                continue
                            if core_cat == "mandatory_exact_matches":
                                continue
                            if course_id in info.get("courses", []):
                                core_hours_collected[core_cat] += G.nodes[course_id].get("credit_hours", 0)
        
        if not semester:
            break

        for course_id_with_suffix in semester:
            base_id = course_id_with_suffix.split('_')[0]
            history.add(base_id)
            remaining_nodes.remove(base_id)
            
        individual.append(semester)
        total_hours += sem_hours
        if not remaining_nodes: break

    if min_utd_per_sem is not None and len(individual) >= 2:
        last_semester = individual[-1]
        previous_semester = individual[-2]
        previous_idx = len(individual) - 2
        if (
            _semester_utd_hours(last_semester, G) < min_utd_per_sem
            and _can_move_semester_courses(last_semester, previous_semester, previous_idx, individual, G, max_hours)
        ):
            previous_semester.extend(last_semester)
            individual.pop()

    return individual


toolbox = base.Toolbox()

def setup_toolbox(G, requirements):
    # Register the individual and population generators
 
    # What changed: Pass `requirements` into the generator so it can bias selections.
    # Why it needed to be changed: generator should know which core buckets are required.
    toolbox.register("individual", tools.initIterate, creator.Individual, lambda: generate_individual(G, requirements=requirements))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

   
    #toolbox.register("evaluate", lambda ind: (evaluate(ind, G, requirements),))
    toolbox.register("evaluate", lambda ind: evaluate(ind, G, requirements))

   
    toolbox.register("mate", tools.cxTwoPoint)
    # Increase mutation index-probability to allow larger shuffles per individual
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.25)
    # Increase tournament size for stronger selection pressure
    toolbox.register("select", tools.selTournament, tournsize=6)

if __name__ == "__main__":
    # 1. Load Data
    try:
        raw_data = load_data_from_json('data_updated2.json')
        with open('requirements.json', 'r') as f:
            requirements = json.load(f)
        G = create_graph(raw_data)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit()

    # 2. Setup the Toolbox with local variables
    setup_toolbox(G, requirements)

    # 3. Running a simple Evolutionary Algorithm 
    # Increased population for broader search
    pop = toolbox.population(n=300)
    # Seed one deterministic near-feasible individual so the GA always starts
    # with a UTD-aware candidate when a minimum per-semester UTD rule is set.
    pop[0] = creator.Individual(generate_individual(G, requirements=requirements, seed_mode=True))
    # Keep a handful of top individuals across runs
    hof = tools.HallOfFame(5)
    
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", lambda x: sum(y[0] for y in x) / len(x))
    stats.register("max", lambda x: max(y[0] for y in x))

    print("Starting Genetic Algorithm Evolution...")
    
    # Run the algorithm
    # What changed: increase number of generations to give the GA more time to
    # converge on feasible schedules.
    # Why it needed to be changed: originally 40 generations was too small given
    # the constrained search space and strict degree audit.
    # Aggressively increase crossover/mutation and generations to explore
    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.85, mutpb=0.45, ngen=500,
                                   stats=stats, halloffame=hof, verbose=True)

    # 4. Display Results
    best_ind = hof[0]
    confirmed_score = evaluate(best_ind, G, requirements, debug=True)[0]
    best_hours = sum(_semester_hours(sem, G) for sem in best_ind)
    population_best = max(pop, key=lambda ind: ind.fitness.values[0])
    print(f"\nBEST SCHEDULE FOUND (Score: {best_ind.fitness.values[0]}):")
    print(f"Confirmed score: {confirmed_score}")
    print(f"Total hours: {best_hours}")
    print(f"Best current-population score: {population_best.fitness.values[0]}")
    print("Hall of Fame scores:", [ind.fitness.values[0] for ind in hof])
    for i, sem in enumerate(best_ind):
        term = "Fall" if i % 2 == 0 else "Spring"
        print(f"Semester {i+1} ({term}): {sem}")
