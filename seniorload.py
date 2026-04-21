import json

with open("data_updated2.json", "r") as f:
    data = json.load(f)

schedule = ["null", "null", "null", "null", "null", "null", "MATH2413", "CS4398"]

score = 0

#assuming indexing starts at 0
#if it is less than an A-

if data[schedule[6]]["difficulty_Score"] > 0.33:
    #this is weighted solution but can also just subtract 8 if hard
    score -= data[schedule[6]]["difficulty_Score"] * 8
if data[schedule[7]]["difficulty_Score"] > 0.33:
    score -= data[schedule[7]]["difficulty_Score"] * 8

print(score)
    