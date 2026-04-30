import json


def normalize_course_id(course_id: str) -> str:
    # What changed: normalize schedule IDs like CS3345_U / CS3345_C -> CS3345.
    # Why: standalone heuristics should safely work with integrated schedule formats.
    if not isinstance(course_id, str):
        return ""
    base = course_id.strip()
    if base.endswith("_U") or base.endswith("_C"):
        return base.rsplit("_", 1)[0]
    return base


def build_prereq_dict(data):
    prereq_count = {}

    for _, course_meta in data.items():
        # What changed: safe prereq read with default [].
        # Why: avoid KeyError if a course has no prereqs key.
        for prereq in course_meta.get("prereqs", []):
            p = normalize_course_id(prereq)
            if p:
                prereq_count[p] = prereq_count.get(p, 0) + 1

    return prereq_count


def calculate_prereq_points(schedule, data, prereq_count, target_sem=6):
    # What changed: local score + target semester gate.
    # Why: reward early completion (keep existing point values).
    score = 0

    # normalized data lookup for safe matching with _U/_C schedule IDs
    data_norm = {normalize_course_id(k): v for k, v in data.items()}

    for i, semester in enumerate(schedule):
        sem_num = i + 1  # 1-based semester number

        # normalize current/prev semester once
        curr_sem = [normalize_course_id(c) for c in semester]
        prev_sem = set(normalize_course_id(c) for c in schedule[i - 1]) if i > 0 else set()

        for course in curr_sem:
            if not course:
                continue

            course_meta = data_norm.get(course, {})

            # Sequential proximity scoring (+4 each match)
            if i > 0:
                prereqs = set(normalize_course_id(p) for p in course_meta.get("prereqs", []))
                # What changed: fixed proximity bug using set intersection.
                # Why: prev_sem and prereqs was boolean-like, not actual overlap count.
                matches = len(prev_sem & prereqs)
                score += matches * 4

            # Prereq points scoring (+2 per dependent prereq), only before target semester
            if sem_num <= target_sem and course in prereq_count:
                score += prereq_count[course] * 2

    return score


if __name__ == "__main__":
    with open("data_updated2.json", "r") as f:
        data = json.load(f)

    # mock schedule
    schedule = [
        ["CS1436", "MATH2413", "ECS1100"],
        ["CS1337", "MATH2414", "PHYS2325+2125", "CS2305"],
        ["CS2340", "PHYS2326+2126", "MATH2418"],
        ["ECS2390", "CS3341", "CS3345", "CS3377"],
        ["CS4337", "CS4341+4141", "CS3354"],
        ["CS4349", "CS3162", "CS4348"],
        ["CS4384", "CS4347"],
        ["CS4485"],
    ]

    prereqs = build_prereq_dict(data)
    score = calculate_prereq_points(schedule, data, prereqs, target_sem=6)
    print(score)