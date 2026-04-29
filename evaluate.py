
import re

DEATH_PENALTY = -10000000

class Tracker:
    def __init__(self, requirements):
        self.history = set()
        self.total_hours = 0
        self.utd_hours = 0
        self.total_cost = 0
        self.total_gpa_points = 0
        self.core_totals = {key: 0 for key in requirements}
        self.semester_difficulty = []

def update_core_totals(course_id, tracker, requirements, graph):
    for core_category, info in requirements.items():
        if course_id in info["courses"]:
            tracker.core_totals[core_category] += graph.nodes[course_id]["credit_hours"]


def _is_cs_4xxx(course_id):
    return re.fullmatch(r"CS4\d{3}", course_id) is not None


def _prereq_satisfied(prereq, course_base_id, history):
    prereq = prereq.strip()
    if not prereq:
        return True

    if prereq == "CS4XXX":
        if course_base_id != "CS4485":
            return False
        completed_cs4xxx = sum(1 for completed_course in history if _is_cs_4xxx(completed_course))
        return completed_cs4xxx >= 3

    if "/" in prereq:
        options = [opt.strip() for opt in prereq.split("/")]
        return any(opt in history for opt in options)

    return prereq in history


def evaluate(individual, G, requirements):
    #history = set()
    #core_totals = {key: 0 for key in requirements}
    tracker = Tracker(requirements)

    # Looping through all the semesters of the entire degree plan
    for i, semester in enumerate(individual):
        sem_hours = 0
        sem_difficulty = 0

        # Looping courses in a semester
        for course_id in semester:
            
            parts = course_id.split('_')
            base_id = parts[0]
            location = parts[1] if len(parts) > 1 else 'U'
            # Invalid course id check:
            if base_id not in G.nodes:
                return (DEATH_PENALTY,)

            # checking if course is already in history
            # if base_id in tracker.history: # changed from course_id to base_id
            #     return (DEATH_PENALTY,)
            seen_this_sem = set()
            for course_id in semester:
                base_id = course_id.split('_')[0]
                if base_id in seen_this_sem:
                    return (DEATH_PENALTY,)
                seen_this_sem.add(base_id)

            data = G.nodes[base_id]
            credits = data.get("credit_hours", 0)
            # Prerequisite check
            prereqs = data["prereqs"]
            for prereq in prereqs:
                if not _prereq_satisfied(prereq, base_id, tracker.history):
                    return (DEATH_PENALTY,)
                
            # Availability check
            term = "Fall" if i % 2 == 0 else "Spring"
            if term not in data["availability"]:
                return (DEATH_PENALTY,)
            if location == 'C':
                tracker.total_cost += (credits * 60) # Collin: $60/hr
            else: # Location is 'U'
                tracker.total_cost += (credits * 1000) # UTD: $1,000/hr
                tracker.total_gpa_points += (data.get("expected_gpa", 4.0) * credits) 
                tracker.utd_hours += credits 
            
            # Update trackers in the loop
            sem_hours += data["credit_hours"]
            sem_difficulty += data["difficulty"]

            # access the tracker class and accounts for requirements.json
            update_core_totals(base_id, tracker, requirements, G)

        # 3. Semester Load/Credit Hours (max 19)
        if sem_hours > 19:
            return (DEATH_PENALTY,)
        
        # Update the tracker class
        tracker.total_hours += sem_hours

        #tracker.history.update(semester)
        for course_id in semester:
            base_id = course_id.split('_')[0]
            tracker.history.add(base_id)

        tracker.semester_difficulty.append(sem_difficulty)

    
    # Normalizing the data
    projected_gpa = tracker.total_gpa_points / tracker.utd_hours if tracker.utd_hours > 0 else 0
    normalized_gpa = projected_gpa / 4.0 * 100

    MAX_POSSIBLE_COST = 120 * 1000 # 120 hours at utd prices
    normalized_cost = ( (MAX_POSSIBLE_COST - tracker.total_cost) / MAX_POSSIBLE_COST ) * 100

    # Checking for total hours requirement (120)
    if tracker.total_hours < 120:
        return (DEATH_PENALTY,)
    
    # Checking Degree Audit
    for core_category, info in requirements.items():
        if tracker.core_totals[core_category] < info["hours_required"]:
            return (DEATH_PENALTY,)
        
    missing_class_penalty = 0
    for category, info in requirements.items():
        # Penalty for missing a mandatory course
        if category == "mandatory_exact_matches":
            for course in info["courses"]:
                if course not in tracker.history:
                    missing_class_penalty += 50000 
                if tracker.core_totals[category] < info["hours_required"]:
                        missing_class_penalty += 50000

    base_score = 100000
    final_score = base_score - missing_class_penalty

    if final_score > 0:
        final_score += normalized_gpa * 500  # GPA is weighted more heavily
        final_score += normalized_cost * 500     # Cost is weighted less heavily
             
    return (final_score,)

        