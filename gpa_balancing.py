import json 

with open('data_updated2.json', 'r') as file:

    data = json.load(file)

def gpa_balancing(individual):
    total_points = 0

    # Looping through each individual semester
    for semesters in individual:
            difficult_classes = 0
            easy_classes = 0
            # Looping through classes
            for classes in semesters:
                if(data[classes]["difficulty_Score"] > 0.85):
                    difficult_classes += 1
                else:
                    easy_classes += 1

            # Penalize if 3 or more classes
            if difficult_classes >= 3:
                total_points -= 10

            # Awards if 0 difficult classes, or balanced ratio
            if difficult_classes == 0:
                 total_points += 5
            else:
                balance_ratio = easy_classes/difficult_classes
                if (0.8 < balance_ratio ):
                     total_points += 5
            
    return (total_points,)