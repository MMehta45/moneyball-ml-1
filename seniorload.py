import json

with open("data_updated2.json", "r") as f:
    data = json.load(f)

schedule = [["CS1436", "MATH2413", "ECS1100"], 
            ["CS1337", "MATH2414", "PHYS2325/2125", "CS2305"],
            ["CS2340", "PHYS2326/2126", "MATH2418"],
            ["ECS2390", "CS3341", "CS3345", "CS3377"],
            ["CS4337", "CS4341/4141", "CS3354"],
            ["CS4349", "CS3162","CS4348"],
            ["CS4384", "CS4347"],
            ["CS4334"]]

score = 0

#assuming indexing starts at 0

for course in schedule[6]:
    if data[course]["difficulty_Score"] > 0.85:
        #this is weighted solution but can also just subtract 8 if hard
        score += round(data[course]["difficulty_Score"] * 8)
for course in schedule[7]:
    if data[course]["difficulty_Score"] > 0.85:
        score += round(data[course]["difficulty_Score"] * 8)

print(score)
    