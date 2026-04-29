import json

with open("data_updated2.json", "r") as f:
    data = json.load(f)

schedule = [["CS1436", "MATH2413", "ECS1100"], 
            ["CS1337", "MATH2414", "PHYS2325+2125", "CS2305"],
            ["CS2340", "PHYS2326+2126", "MATH2418"],
            ["ECS2390", "CS3341", "CS3345", "CS3377"],
            ["CS4337", "CS4341+4141", "CS3354"],
            ["CS4349", "CS3162","CS4348"],
            ["CS4384", "CS4347"],
            ["CS4334"]]

def senior_load_reduction(schedule, data):
    # What changed: Removed global score dependency and compute penalty internally.
    # Why it needed to be changed: Keeps the function standalone and deterministic.
    hard_class_count = 0

    # What changed: Scan only senior year semesters 7 and 8 (indices 6 and 7) when present.
    # Why it needed to be changed: Prevents index errors for shorter schedules.
    for semester_index in (6, 7):
        if semester_index >= len(schedule):
            continue

        for course in schedule[semester_index]:
            # What changed: Added safe lookup for missing courses.
            # Why it needed to be changed: Avoids crashes when a course is not in data.
            course_data = data.get(course)
            if not isinstance(course_data, dict):
                continue

            # What changed: Added type-safe difficulty handling.
            # Why it needed to be changed: Missing/non-numeric values should be treated as not hard.
            difficulty_score = course_data.get("difficulty_Score")
            if not isinstance(difficulty_score, (int, float)):
                continue

            if difficulty_score > 0.85:
                hard_class_count += 1

    return int(-8 * hard_class_count)


penalty = senior_load_reduction(schedule, data)
print(penalty)