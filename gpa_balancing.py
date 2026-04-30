def _normalize_course_id(course_id):
    if not isinstance(course_id, str):
        return ""
    value = course_id.strip()
    if value.endswith("_U") or value.endswith("_C"):
        return value.rsplit("_", 1)[0]
    return value


def _semester_difficulty_counts(semester, course_data):
    difficult_classes = 0
    easy_classes = 0

    for course in semester:
        course_id = _normalize_course_id(course)
        info = course_data.get(course_id)
        if not isinstance(info, dict):
            continue
        difficulty_score = info.get("difficulty_Score")
        if not isinstance(difficulty_score, (int, float)):
            continue
        if difficulty_score > 0.85:
            difficult_classes += 1
        else:
            easy_classes += 1

    return difficult_classes, easy_classes


def burnout_penalty(individual, course_data):
    total_points = 0

    for semester in individual:
        difficult_classes, _ = _semester_difficulty_counts(semester, course_data)
        if difficult_classes >= 3:
            total_points -= 10

    return (total_points,)


def balance_reward(individual, course_data):
    total_points = 0

    for semester in individual:
        difficult_classes, easy_classes = _semester_difficulty_counts(semester, course_data)
        if difficult_classes == 0:
            total_points += 5
        else:
            balance_ratio = easy_classes / difficult_classes
            if 0.8 < balance_ratio:
                total_points += 5

    return (total_points,)


def gpa_balancing(individual, course_data):
    return (burnout_penalty(individual, course_data)[0] + balance_reward(individual, course_data)[0],)
