import json
from collections import Counter

with open("data.json", "r") as f:
    data = json.load(f)

schedule = ["CS1436", "CS1337"]

score = 0

#what about freshman classes with no prerequisites
#parse through and count how many classes its a prereq for

prereq_count = {}

for courses in data:
    for prereq in data[courses]["prereqs"]:
        prereq_count[prereq] = 1 + prereq_count.get(prereq, 0)

#for schedule in shcedules:
for i, course in enumerate(schedule):
    if i != 0 and schedule[i-1] in data[course]["prereqs"]:
        score += 4
    score += prereq_count[course] * 2

print(score)

