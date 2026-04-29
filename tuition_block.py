import json 

with open("data_updated2.json", "r") as file:
    data = json.load(file)

def tuition_block(individual):
    total_points = 0

    for semesters in individual:
        utd_credits = 0

        # What changed: Count UTD credits instead of total semester credits.
        # Why: The tuition-block reward should reflect hitting the UTD tuition threshold.
        for classes in semesters:
            if classes.split("_")[1] == "U":
                utd_credits += data[classes.split("_")[0]]["credit_hours"]

        # What changed: Reward semesters that reach 12+ UTD credit hours.
        # Why: This matches the tuition block rule more closely than total credits.
        if utd_credits >= 12:
            total_points += 5

    return (total_points, )