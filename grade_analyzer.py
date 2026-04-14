# Grade point mapping
grade_points = {
    "A": 4.0,
    "A-": 3.67,
    "B+": 3.33,
    "B": 3.0,
    "B-": 2.67,
    "C+": 2.33,
    "C": 2.0,
    "C-": 1.67,
    "D+": 1.33,
    "D": 1.0,
    "F": 0.0
}

# Mean GPA per course pulled from UTD Trends (hover over overall grade distribution)
# None = no data available on UTD Trends for any semester
class_grade_distributions = {
    # Izma: RHET 1302 - CS 4141
    "ECS 1100":  3.54,
    "CS 1200":   3.46,
    "CS 1436":   2.82,
    "CS 1337":   2.92,
    "CS 2305":   2.96,
    "CS 2336":   3.18,
    "GOVT 2305": 3.14,
    "MATH 2418": 2.58,
    "RHET 1302": 3.23,
    "PHYS 2125": 3.76,
    "PHYS 2126": 3.77,
    "PHYS 2325": 3.16,
    "PHYS 2326": 3.05,
    "MATH 2413": 2.33,
    "MATH 2414": 2.41,
    "MATH 2417": 2.36,
    "MATH 2419": 2.52,
    "CS 3162":   3.63,
    "CS 3341":   2.87,
    "CS 3345":   3.25,
    "CS 3354":   3.41,
    "CS 3377":   3.20,
    "ECS 2390":  3.46,
    "CS 4141":   3.71,
    "Language, Philosophy, and Culture": 3.10,
    "Creative Arts":                     3.38,
    "American History":                  3.21,
    "Social and Behavioral Sciences":    3.19,

    # Sadwitha: CS 4337 - SE 4381
    "CS 4337": 3.096,
    "CS 4341": 3.154,
    "CS 4347": 3.341,
    "CS 4348": 2.988,
    "CS 4384": 3.124,
    "CS 4385": None,
    "CS 4314": 3.030,
    "CS 4315": 3.303,
    "CS 4332": 3.763,
    "CS 4334": 2.826,
    "CS 4336": 3.243,
    "CS 4339": None,
    "CS 4352": 3.757,
    "CS 4361": 3.228,
    "CS 4365": 3.107,
    "CS 4375": 3.244,
    "CS 4376": 3.038,
    "CS 4386": 2.795,
    "CS 4389": 3.299,
    "CS 4390": 3.051,
    "CS 4391": 3.240,
    "CS 4392": 3.187,
    "CS 4393": 2.954,
    "CS 4394": 3.333,
    "CS 4395": 3.423,
    "CS 4396": 3.166,
    "CS 4397": 3.207,
    "CS 4398": 3.128,
    "CS 4399": None,
    "CS 4359": 3.822,
    "EE 4325": 3.076,
    "SE 4351": 3.299,
    "SE 4352": 3.301,
    "SE 4367": 2.936,
    "SE 4381": 3.267,
}


def calculate_expected_gpa(distribution):
    # distribution is now a direct mean GPA float (or None)
    return distribution


def calculate_difficulty(expected_gpa):
    if expected_gpa is None:
        return None
    return expected_gpa - 4.0   # as per your requirement


# Store results
course_results = {}

for course, distribution in class_grade_distributions.items():
    expected_gpa = calculate_expected_gpa(distribution)
    difficulty = calculate_difficulty(expected_gpa)

    course_results[course] = {
        "expected_gpa": expected_gpa,
        "difficulty_score": difficulty
    }


# Example output
for course, data in course_results.items():
    print(course, "->", data)
