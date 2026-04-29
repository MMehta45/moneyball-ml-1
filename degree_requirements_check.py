def degree_requirements_check(schedule, required_courses):
    score = 0
    completed_courses = []

    # collect all courses in the schedule
    for semester in schedule:
        for course in semester:
            completed_courses.append(course.get("id"))

    # check if each required course is completed
    for required_course in required_courses:
        if required_course in completed_courses:
            score += 5
        else:
            score -= 10

    return score
