import random
import networkx as nx
import json
from evaluate import evaluate, DEATH_PENALTY


def generate_individual(G, max_semesters=12, max_hours=19):
    individual = []
    history = set()
    remaining_nodes = set(G.nodes())
    
    for sem_idx in range(max_semesters):
        semester = []
        sem_hours = 0
        term = "Fall" if sem_idx % 2 == 0 else "Spring"
        
        candidates = []
        for node in remaining_nodes:
            node_data = G.nodes[node]
            node_prereqs = node_data.get("prereqs", [])
            
            prereqs_met = True
            for p in node_prereqs:
                if not p or p.strip() == "": continue
                
                
                if "/" in p:
                    options = [opt.strip() for opt in p.split("/")]
                   
                    if not any(opt in history or opt not in G.nodes for opt in options):
                        prereqs_met = False
                        break
                else:
                   
                    if p in G.nodes and p not in history:
                        prereqs_met = False
                        break
            
            # Check availability
            available_now = term in node_data.get("availability", [])
            
            if prereqs_met and available_now:
                candidates.append(node)
        
        random.shuffle(candidates)
        
        for course_id in candidates:
            course_hours = G.nodes[course_id].get("credit_hours", 0)
            if sem_hours + course_hours <= max_hours:
                semester.append(course_id)
                sem_hours += course_hours
        
        for course_id in semester:
            history.add(course_id)
            remaining_nodes.remove(course_id)
            
        individual.append(semester)
        if not remaining_nodes: break
            
    return individual
from create_graph import load_data_from_json, create_graph

if __name__ == "__main__":
    try:
        raw_data = load_data_from_json('data_updated2.json')
        with open('requirements.json', 'r') as f:
            requirements = json.load(f)
            
        G = create_graph(raw_data)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit()

    found_valid = False
    attempts = 0
    max_attempts = 1000
    
    print(f"Attempting to generate a valid schedule for {len(G.nodes)} courses...")

    while not found_valid and attempts < max_attempts:
        attempts += 1
        
        
        candidate = generate_individual(G)
        
       
        score = evaluate(candidate, G, requirements)
        
        if score == 1: # changed from !=DEATH_PENALTY to ==1
            print(f" VALID SCHEDULE FOUND on attempt {attempts}")
            for i, sem in enumerate(candidate):
                term = "Fall" if i % 2 == 0 else "Spring"
                print(f"Semester {i+1} ({term}): {sem}")
            found_valid = True
            
    if not found_valid:
        print(f"Failed to find a valid schedule")
