import json

# Difficulty Classification Thresholds
# easy     : difficulty_Score < 0.75
# moderate : 0.75 <= difficulty_Score <= 0.85  
# hard     : difficulty_Score > 0.85

DIFFICULTY_EASY_MAX = 0.75
DIFFICULTY_HARD_MIN = 0.85
DIFFICULTY_AVERAGE  = 0.80   # representative midpoint of the moderate band

def classify_difficulty(score: float) -> str:
    """Return a human-readable difficulty label for a given difficulty_Score."""
    if score < DIFFICULTY_EASY_MAX:
        return "easy"
    elif score > DIFFICULTY_HARD_MIN:
        return "hard"
    else:
        return "moderate"   # 0.75 - 0.85


# Data Loading (reused from create_graph.py)
def load_data_from_json(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
        data = {}
        for course_id, course in json_data.items():
            difficulty = course.get("difficulty_score", course.get("difficulty_Score"))
            data[course_id] = {
                "name": course["name"],
                "credit_hours": course["credit_hours"],
                "prereqs": course["prereqs"],
                "is_transferable": course["is_transferable"],
                "availability": course["availability"],
                "difficulty_Score": difficulty,
                "difficulty_label": classify_difficulty(difficulty) if difficulty is not None else "unknown",
                "expected_gpa": course["expected_gpa"]
            }
        return data



# Internship Readiness
INTERNSHIP_CRITICAL_COURSES = {
    "CS3345", # Data Structures & Algorithm Analysis
    "CS2336", # Computer Science II 
    "CS3354", # Software Engineering
    "CS4348", # Operating Systems
    "CS4347", # Database Systems
    "CS4349", # Advanced Algorithm Design & Analysis
}

JUNIOR_YEAR_END_SEMESTER = 6   # semesters 5-6 = junior year in an 8-sem plan

def check_internship_readiness(semester_plan: dict) -> dict:
   
    # Build a lookup: course_id -> earliest semester it appears in the plan
    # What changed: Track the first semester for each course.
    # Why: We need to know whether a critical course was finished by semester 6.
    completion_map = {}
    for sem, courses in semester_plan.items():
        for cid in courses:
            if cid not in completion_map:
                completion_map[cid] = sem

    completed_by = {}
    completed_early = []
    missing = []

    for cid in INTERNSHIP_CRITICAL_COURSES:
        sem = completion_map.get(cid)
        completed_by[cid] = sem
        if sem is None:
            missing.append(cid)
        elif sem <= JUNIOR_YEAR_END_SEMESTER:
            # What changed: Count each critical course completed on time.
            # Why: Internship readiness should reward progress course-by-course.
            completed_early.append(cid)

    # What changed: Score per early course instead of all-or-nothing.
    # Why: Partial internship prep should still be rewarded.
    earned = len(completed_early) > 0
    score  = len(completed_early)

    if completed_early:
        explanation = (
            f" Internship Readiness: +{score} points\n"
            f" {len(completed_early)} internship critical course(s) are completed by "
            f"the end of semester {JUNIOR_YEAR_END_SEMESTER} (junior year)."
        )
    else:
        explanation = (
            " Internship Readiness: +0 points\n"
            f" No internship critical courses are completed by semester "
            f"{JUNIOR_YEAR_END_SEMESTER}.\n"
            # What changed: Show which critical courses are still missing.
            # Why: This makes the result easier to debug.
            + "\n".join(f"     - {c} (completed in semester {completed_by[c] or 'never'})"
                        for c in missing)
        )

    return {
        "score":        score,
        "earned":       earned,
        "completed_early": completed_early,
        "completed_by": completed_by,
        "missing":      missing,
        "explanation":  explanation,
    }



# Freshman Buffer

HEAVY_THRESHOLD   = DIFFICULTY_HARD_MIN  # difficulty_Score strictly above 0.85 -> "hard/heavy"
HEAVY_COUNT_LIMIT = 3                    # must have FEWER than this many heavy courses

FRESHMAN_SEMESTERS = [1, 2]

def check_freshman_buffer(semester_plan: dict, course_data: dict) -> dict:
    heavy_courses = []

    for sem in FRESHMAN_SEMESTERS:
        courses_this_sem = semester_plan.get(sem, [])
        for cid in courses_this_sem:
            info = course_data.get(cid)
            if info is None:
                continue  
            diff = info.get("difficulty_Score")
            if not isinstance(diff, (int, float)):
                continue
            if diff > HEAVY_THRESHOLD:
                heavy_courses.append((cid, info["name"], diff, sem))

    total_heavy = len(heavy_courses)
    earned = total_heavy <= HEAVY_COUNT_LIMIT
    score  = 6 if earned else 0

    if earned:
        explanation = (
            f" Freshman Buffer: +6 points\n"
            f" Only {total_heavy} hard course(s) (difficulty > {HEAVY_THRESHOLD}, i.e. 'hard') "
            f"detected in freshman year — below the limit of {HEAVY_COUNT_LIMIT}.\n"
            f" Difficulty scale: easy < {DIFFICULTY_EASY_MAX} | "
            f"moderate {DIFFICULTY_EASY_MAX}–{DIFFICULTY_HARD_MIN} (avg ≈ {DIFFICULTY_AVERAGE}) | "
            f"hard > {DIFFICULTY_HARD_MIN}"
        )
    else:
        explanation = (
            f" Freshman Buffer: +0 points\n"
            f"  {total_heavy} hard course(s) found in freshman year \n"
            + "\n".join(
                f"     - Sem {sem}: {cid} — {name} "
                f"(difficulty {diff:.3f} -> {classify_difficulty(diff)})"
                for cid, name, diff, sem in heavy_courses
            )
        )

    return {
        "score":        score,
        "earned":       earned,
        "heavy_courses": heavy_courses,
        "total_heavy":  total_heavy,
        "explanation":  explanation,
    }

# Combined scorer
def evaluate_plan(semester_plan: dict, course_data: dict) -> dict:
    
    internship = check_internship_readiness(semester_plan)
    freshman   = check_freshman_buffer(semester_plan, course_data)

    total = internship["score"] + freshman["score"]

    print()
    print("---- DEGREE PLAN HEURISTIC EVALUATION ----")
    print()
    print(internship["explanation"])
    print()
    print(freshman["explanation"])
    print()
    print(f"---- TOTAL SCORE FROM THESE TWO HEURISTICS: {total} / 12 ----")
    print()

    return {
        "internship_readiness": internship,
        "freshman_buffer":      freshman,
        "total_score":          total,
    }

# Demo / quick test
if __name__ == "__main__":
    # Load the course catalog
    course_data = load_data_from_json("data_updated2.json")


    example_plan = {
        # Freshman Year 
        1: ["CS1436", "ECS1100", "CS1200", "RHET1302", "GOVT2305"],   # all easy/moderate
        2: ["CS1337", "MATH2413", "GOVT2306"],                         # MATH2413 is heavy (1.67)

        # Sophomore Year
        3: ["CS2336", "CS2305", "MATH2414", "PHYS2325/2125"],
        4: ["CS2340", "PHYS2326/2126", "MATH2418", "ECS2390"],

        # Junior Year
        5: ["CS3345","CS3341", "CS3354", "CS3377"],
        6: ["CS4348", "CS4347", "CS4349", "CS4337"],   # all internship critical done by sem 6 

        # Senior Year
        7: ["CS4341/4141", "CS4384", "CS4375", "CS3162"],
        8: ["CS4485", "CS4365", "CS4390", "CS4376"],
    }

    results = evaluate_plan(example_plan, course_data)