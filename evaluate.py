
import re
from heuristics_adapter import compute_heuristics_breakdown

DEATH_PENALTY = -10000000

class Tracker:
    def __init__(self, requirements):
        self.history = set()
        self.total_hours = 0
        self.utd_hours = 0
        self.total_cost = 0
        self.total_gpa_points = 0
        self.core_totals = {key: 0 for key in requirements}
        self.semester_difficulty = []
        # Track per-semester totals for hours and UTD hours
        self.hours_by_sem = []
        self.utd_hours_by_sem = []

def update_core_totals(course_id, tracker, requirements, graph):
    for core_category, info in requirements.items():
        if not isinstance(info, dict):
            continue
        # What changed: Skip mandatory_exact_matches when accumulating core hour totals.
        # Why it needed to be changed: mandatory_exact_matches is a presence-based graduation rule, not a core-hour bucket.
        if core_category == "mandatory_exact_matches":
            continue
        if course_id in info["courses"]:
            tracker.core_totals[core_category] += graph.nodes[course_id]["credit_hours"]


def _core_requirement_categories(requirements):
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


def _format_score(value):
    return f"{value:.2f}" if isinstance(value, float) else str(value)


def _print_evaluation_debug(
    final_score,
    base_score,
    normalized_gpa,
    normalized_cost,
    missing_class_penalty,
    extra_hours_penalty,
    senior_core_penalty,
    fully_core_penalty,
    senior_core_class_count,
    core_counts_by_sem,
    tracker,
    heuristics_breakdown,
):
    print("\n---- EVALUATION DEBUG ----")
    print(f"Final score: {_format_score(final_score)}")
    print(f"Base score: {base_score}")
    print(f"Total hours: {tracker.total_hours}")
    print(f"UTD hours: {tracker.utd_hours}")
    print(f"Semester hours: {tracker.hours_by_sem}")
    print(f"Semester UTD hours: {tracker.utd_hours_by_sem}")
    print(f"Normalized GPA contribution: {_format_score(normalized_gpa * 500)}")
    print(f"Normalized cost contribution: {_format_score(normalized_cost * 500)}")
    print(f"Missing mandatory penalty: -{missing_class_penalty}")
    print(f"Extra hours penalty: -{extra_hours_penalty}")
    print(f"Senior core count: {senior_core_class_count}")
    print(f"Senior core penalty: -{senior_core_penalty}")
    print(f"Core counts by semester: {core_counts_by_sem}")
    print(f"Fully-core semester penalty: -{fully_core_penalty}")
    print("Heuristic components:")
    for name, score in heuristics_breakdown["components"].items():
        print(f"  {name}: {_format_score(score)}")
    print(f"Heuristic total: {_format_score(heuristics_breakdown['total'])}")
    print("--------------------------\n")


def _is_cs_4xxx(course_id):
    return re.fullmatch(r"CS4\d{3}", course_id) is not None


def _prereq_satisfied(prereq, course_base_id, history):
    prereq = prereq.strip()
    if not prereq:
        return True

    if prereq == "CS4XXX":
        if course_base_id != "CS4485":
            return False
        completed_cs4xxx = sum(1 for completed_course in history if _is_cs_4xxx(completed_course))
        return completed_cs4xxx >= 3

    if "/" in prereq:
        options = [opt.strip() for opt in prereq.split("/")]
        return any(opt in history for opt in options)

    return prereq in history


def evaluate(individual, G, requirements, debug=False):
    #history = set()
    #core_totals = {key: 0 for key in requirements}
    tracker = Tracker(requirements)
    senior_core_class_count = 0
    core_counts_by_sem = []
    fully_core_semester_count = 0

    # Looping through all the semesters of the entire degree plan
    for i, semester in enumerate(individual):
        sem_hours = 0
        sem_difficulty = 0
        sem_utd_hours = 0
        sem_utd_billable_hours = 0
        sem_core_class_count = 0

        # What changed: Move the duplicate-course check outside the per-course validation body.
        # Why it needed to be changed: resetting the set inside the inner loop can repeat work and hide duplicate detection bugs.
        seen_this_sem = set()
        for semester_course_id in semester:
            base_semester_id = semester_course_id.split('_')[0]
            if base_semester_id in seen_this_sem:
                return (DEATH_PENALTY,)
            seen_this_sem.add(base_semester_id)

        # Looping courses in a semester
        for course_id in semester:
            
            parts = course_id.split('_')
            base_id = parts[0]
            location = parts[1] if len(parts) > 1 else 'U'
            # Invalid course id check:
            if base_id not in G.nodes:
                return (DEATH_PENALTY,)

            data = G.nodes[base_id]
            credits = data.get("credit_hours", 0)
            # Prerequisite check
            prereqs = data["prereqs"]
            for prereq in prereqs:
                if not _prereq_satisfied(prereq, base_id, tracker.history):
                    return (DEATH_PENALTY,)
                
            # Availability check
            term = "Fall" if i % 2 == 0 else "Spring"
            if term not in data["availability"]:
                return (DEATH_PENALTY,)
            if location == 'C':
                tracker.total_cost += (credits * 60)
            else: # Location is 'U'
                # What changed: Cap UTD tuition once the semester reaches 12 UTD hours.
                # Why: The tuition-block rule should stop charging after the block is full.
                billable_utd_hours = min(credits, max(0, 12 - sem_utd_billable_hours))
                tracker.total_cost += (billable_utd_hours * 1000)
                tracker.total_gpa_points += (data.get("expected_gpa", 4.0) * credits) 
                tracker.utd_hours += credits 
                sem_utd_hours += credits
                sem_utd_billable_hours += billable_utd_hours
            
            # Update trackers in the loop
            sem_hours += data["credit_hours"]
            sem_difficulty += data["difficulty"]

            # access the tracker class and accounts for requirements.json
            update_core_totals(base_id, tracker, requirements, G)

            # What changed: Count core courses in senior year (semesters 7 and 8) only.
            # Why it needed to be changed: we want to cap core-heavy senior schedules without counting technical electives.
            if _is_core_course(base_id, requirements):
                sem_core_class_count += 1

            if i >= 6 and _is_core_course(base_id, requirements):
                senior_core_class_count += 1

        # 3. Semester Load/Credit Hours (max 19)
        if sem_hours > 19:
            return (DEATH_PENALTY,)
        
        # Update the tracker class
        tracker.total_hours += sem_hours
        tracker.hours_by_sem.append(sem_hours)
        tracker.utd_hours_by_sem.append(sem_utd_hours)
        core_counts_by_sem.append(sem_core_class_count)
        if semester and sem_core_class_count == len(semester):
            fully_core_semester_count += 1

        #tracker.history.update(semester)
        for course_id in semester:
            base_id = course_id.split('_')[0]
            tracker.history.add(base_id)

        tracker.semester_difficulty.append(sem_difficulty)

    
    # Normalizing the data
    projected_gpa = tracker.total_gpa_points / tracker.utd_hours if tracker.utd_hours > 0 else 0
    normalized_gpa = projected_gpa / 4.0 * 100

    MAX_POSSIBLE_COST = 120 * 1000 # 120 hours at utd prices
    normalized_cost = ( (MAX_POSSIBLE_COST - tracker.total_cost) / MAX_POSSIBLE_COST ) * 100

    # Checking for total hours requirement (120)
    if tracker.total_hours < 120:
        return (DEATH_PENALTY,)
    if tracker.total_hours > 125:
        return (DEATH_PENALTY,)

    extra_hours = max(0, tracker.total_hours - 120)
    extra_hours_penalty = extra_hours * 12000

    senior_core_overage = max(0, senior_core_class_count - 3)
    senior_core_penalty = senior_core_overage * 25000
    fully_core_penalty = fully_core_semester_count * 75000

    # Enforce minimum UTD hours per semester if specified in requirements
    min_utd_per_sem = requirements.get("min_utd_hours_per_sem", None)
    if min_utd_per_sem is not None:
        for sem_idx, sem_utd in enumerate(tracker.utd_hours_by_sem):
            if sem_utd < min_utd_per_sem:
                return (DEATH_PENALTY,)
    
    # Checking Degree Audit
    for core_category, info in requirements.items():
        if not isinstance(info, dict):
            continue
        # What changed: Skip mandatory_exact_matches in the generic hours-based core audit.
        # Why it needed to be changed: mandatory_exact_matches must be validated by exact course presence, not by hour totals.
        if core_category == "mandatory_exact_matches":
            continue
        if tracker.core_totals[core_category] < info["hours_required"]:
            return (DEATH_PENALTY,)
        
    missing_class_penalty = 0
    for category, info in requirements.items():
        if not isinstance(info, dict):
            continue
        # Penalty for missing a mandatory course
        if category == "mandatory_exact_matches":
            # What changed: Check all mandatory_exact_matches courses together and apply the penalty only once.
            # Why it needed to be changed: mandatory courses must all be present, and repeating the penalty per course inflated the score penalty.
            missing_mandatory_courses = [course for course in info["courses"] if course not in tracker.history]
            if missing_mandatory_courses:
                missing_class_penalty += 50000

    base_score = 100000
    final_score = base_score - missing_class_penalty - extra_hours_penalty - senior_core_penalty - fully_core_penalty

    if final_score > 0:
        final_score += normalized_gpa * 500  # GPA is weighted more heavily
        final_score += normalized_cost * 500     # Cost is weighted less heavily

    # Add signed heuristic deltas (rewards and penalties) from standalone scoring modules.
    heuristics_breakdown = compute_heuristics_breakdown(individual, G)
    final_score += heuristics_breakdown["total"]

    if debug:
        _print_evaluation_debug(
            final_score,
            base_score,
            normalized_gpa,
            normalized_cost,
            missing_class_penalty,
            extra_hours_penalty,
            senior_core_penalty,
            fully_core_penalty,
            senior_core_class_count,
            core_counts_by_sem,
            tracker,
            heuristics_breakdown,
        )
             
    return (final_score,)

        
