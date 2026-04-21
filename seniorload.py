import json

with open("data.json", "r") as f:
    data = json.load(f)

schedule = ["null", "null", "null", "null", "null", "null", "CS1436", "CS1337"]

score = 0

#assuming indexing starts at 0
#if it is less than an A-
if data[schedule[6]]["difficulty_score"] > 0.33:
    #this is weighted solution but can also just subtract 8 if hard
    score -= data[schedule[6]]["difficulty_score"] * 10
if data[schedule[7]]["difficulty_score"] > 0.33:
    score -= data[schedule[6]]["difficulty_score"] * 10
    