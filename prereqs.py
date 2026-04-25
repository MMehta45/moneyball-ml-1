import json

with open("data_updated2.json", "r") as f:
    data = json.load(f)

#mock schedule    
schedule = [["CS1436", "MATH2413", "ECS1100"], 
            ["CS1337", "MATH2414", "PHYS2325/2125", "CS2305"],
            ["CS2340", "PHYS2326/2126", "MATH2418"],
            ["ECS2390", "CS3341", "CS3345", "CS3377"],
            ["CS4337", "CS4341/4141", "CS3354"],
            ["CS4349", "CS3162","CS4348"],
            ["CS4384", "CS4347"],
            ["CS4485"]]

score = 0

def build_prereq_dict(data):
    prereq_count = {}

    for courses in data:
        for prereq in data[courses]["prereqs"]:
            prereq_count[prereq] = 1 + prereq_count.get(prereq, 0)
    
    return prereq_count
    
def calculate_prereq_points(schedule, data, prereq_count, score):
    #global score
    #for schedule in schedules:
    for i, semester in enumerate(schedule):
        for course in semester:
            #sequential proximity scoring
            #are any of the prereqs taken in the semester before
            if i != 0:
                prev_sem = set(schedule[i-1])
                prereqs = set(data[course]["prereqs"])
                matches = len(prev_sem and prereqs)
                score += matches * 4
            
            #prereq points scoring
            if course in prereq_count:
                score += prereq_count[course] * 2
    return score

prereqs = build_prereq_dict(data)
score = calculate_prereq_points(schedule, data, prereqs, score)
print(score)

