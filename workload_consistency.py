from statistics import pstdev


def workload_consistency(schedule, course_data=None):
    semester_credits = []

    for semester in schedule:
        total_credits = 0

        for course in semester:
            if isinstance(course, dict):
                total_credits += course.get("credits", course.get("credit_hours", 0))
            elif isinstance(course, str) and isinstance(course_data, dict):
                info = course_data.get(course)
                if isinstance(info, dict):
                    total_credits += info.get("credit_hours", info.get("credits", 0))

        semester_credits.append(total_credits)

    if len(semester_credits) < 2:
        return 0

    # Penalize variability across semesters: higher spread means less consistent workload.
    return -3 * pstdev(semester_credits)
