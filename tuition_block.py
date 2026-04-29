import json 

with open("data_updated2.json", "r") as file:
    data = json.load(file)

def tuition_block(individual):
    total_points = 0

    for semesters in individual:
        total_credits = 0

        # Adding up total credits
        for classes in semesters:
            total_credits += data[classes]["credit_hours"]

        # If semester has 12 or more credits
        if total_credits >= 12:
            total_points += 5

    return (total_points, )