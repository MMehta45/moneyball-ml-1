def tuition_block(individual, course_data):
    total_points = 0

    for semesters in individual:
        utd_credits = 0

        # What changed: Count UTD credits instead of total semester credits.
        # Why: The tuition-block reward should reflect hitting the UTD tuition threshold.
        for classes in semesters:
            if not isinstance(classes, str):
                continue
            parts = classes.split("_")
            if len(parts) < 2:
                continue
            if parts[1] == "U":
                base_id = parts[0]
                info = course_data.get(base_id)
                if not isinstance(info, dict):
                    continue
                utd_credits += info.get("credit_hours", 0)

        # What changed: Reward semesters that reach 12+ UTD credit hours.
        # Why: This matches the tuition block rule more closely than total credits.
        if utd_credits >= 12:
            total_points += 5

    return (total_points, )