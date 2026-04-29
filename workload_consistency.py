def workload_consistency(schedule):
    score = 0

    # I used 15 credits as a normal full-time semester
    ideal_credits = 15

    for semester in schedule:
        semester_credits = 0

        for course in semester:
            semester_credits += course.get("credits", 0)

        # checks how far the semester is from 15 credits
        difference = abs(semester_credits - ideal_credits)

        # if the semester is way too light or heavy, subtract points
        if difference > 3:
            score -= difference * 2

    return score
