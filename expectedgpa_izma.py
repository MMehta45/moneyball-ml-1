# Stored in JSON data structure
# JSON[course name][expected_gpa] = the number
# JSON[course name][difficulty score] = the number
# method: average grades

import json

# assume json is called x
with open("courses.json", "r") as f:
    courses = json.load(f)



#develop a function that just takes class name and grade
#it converts each grade to the number and inputs it into courses and then also 
#does difficulty score --> create an array

def calculate_gpa(class_name):
    if class_name in courses and class_name in class_grades:
        grade = class_grades[class_name]
        courses[class_name]["expected_gpa"] = grade
        courses[class_name]["difficulty_score"] = 4.0 - grade


class_grades = {
    "ECS 1100" : 3.54,
    "CS 1200" : 3.46,
    "CS 1436" : 2.82,
    "CS 1337" : 2.92,
    "CS 2305" : 2.96,
    "CS 2336" : 3.18,
    "GOVT 2305" : 3.14,
    "MATH 2418" : 2.58,
    "RHET 1302" : 3.23,
    "PHYS 2125" : 3.76,
    "PHYS 2126" : 3.77,
    "PHYS 2325" : 3.16,
    "PHYS 2326" : 3.05,
    "MATH 2413" : 2.33,
    "MATH 2414" : 2.41,
    "MATH 2417" : 2.36,
    "MATH 2419" : 2.52,
    "CS 3162" : 3.63,
    "CS 3341" : 2.87,
    "CS 3345" : 3.25,
    "CS 3354" : 3.41,
    "CS 3377" : 3.20,
    "ECS 2390" : 3.46,
    "CS 4141" : 3.71,
    "Language, Philosophy, and Culture" : 3.10,
    "Creative Arts" : 3.38,
    "American History" : 3.21,
    "Social and Behavioral Sciences" : 3.19,
}

for course in class_grades:
    calculate_gpa(course)


with open("courses.json", "w") as f:
    json.dump(courses, f, indent=4)