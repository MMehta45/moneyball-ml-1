
DEATH_PENALTY = -10000000

class Tracker:
    def __init__(self, requirements):
        self.history = set()
        self.total_hours = 0
        self.core_totals = {key: 0 for key in requirements}
        self.semester_difficulty = []

def update_core_totals(course_id, tracker, requirements, graph):
    for core_category, info in requirements.items():
        if course_id in info["courses"]:
            tracker.core_totals[core_category] += graph.nodes[course_id]["credit_hours"]


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

            # Invalid course id check:
            if course_id not in G.nodes:
                return DEATH_PENALTY

            # checking if course is already in history
            if course_id in tracker.history:
                return DEATH_PENALTY

            data = G.nodes[course_id]

            # Prerequisite check
            # prereqs = data["prereqs"]
            # for prereq in prereqs:
            #     if prereq not in tracker.history:
            #         return DEATH_PENALTY
                
            # Availability check
            term = "Fall" if i % 2 == 0 else "Spring"
            if term not in data["availability"]:
                return DEATH_PENALTY
            
            # Update trackers in the loop
            sem_hours += data["credit_hours"]
            sem_difficulty += data["difficulty"]

            # access the tracker class and accounts for requirements.json
            update_core_totals(course_id, tracker, requirements, G)

        # 3. Semester Load/Credit Hours (max 19)
        if sem_hours > 19:
            return DEATH_PENALTY
        
        # Update the tracker class
        tracker.total_hours += sem_hours
        tracker.history.update(semester)
        tracker.semester_difficulty.append(sem_difficulty)

    
    # Checking for total hours requirement (120)
    if tracker.total_hours < 120:
        return DEATH_PENALTY
    
    # Checking Degree Audit
    # for core_category, info in requirements.items():
    #     if tracker.core_totals[core_category] < info["hours_required"]:
    #         return DEATH_PENALTY
        

    return (1,)

        





