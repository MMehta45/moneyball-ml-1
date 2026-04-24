import random
import networkx as nx
import json
from deap import base, creator, tools, algorithms
from evaluate import evaluate, DEATH_PENALTY
from create_graph import load_data_from_json, create_graph


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

def generate_individual(G, max_semesters=8, max_hours=19):
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
            
            available_now = term in node_data.get("availability", [])
            if prereqs_met and available_now:
                candidates.append(node)
        
        random.shuffle(candidates)
        for course_id in candidates:
            course_hours = G.nodes[course_id].get("credit_hours", 0)
            if sem_hours + course_hours <= max_hours:
                is_transferable = G.nodes[course_id].get("transferable", False)
                suffix = random.choice(["_U", "_C"]) if is_transferable else "_U"
                semester.append(f"{course_id}{suffix}")
                sem_hours += course_hours
        
        for course_id_with_suffix in semester:
            base_id = course_id_with_suffix.split('_')[0]
            history.add(base_id)
            remaining_nodes.remove(base_id)
            
        individual.append(semester)
        if not remaining_nodes: break
            
    return individual


toolbox = base.Toolbox()

def setup_toolbox(G, requirements):
    # Register the individual and population generators
 
    toolbox.register("individual", tools.initIterate, creator.Individual, lambda: generate_individual(G))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

   
    toolbox.register("evaluate", lambda ind: (evaluate(ind, G, requirements),))

   
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

if __name__ == "__main__":
    # 1. Load Data
    try:
        raw_data = load_data_from_json('data_updated2.json')
        with open('requirements.json', 'r') as f:
            requirements = json.load(f)
        G = create_graph(raw_data)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit()

    # 2. Setup the Toolbox with local variables
    setup_toolbox(G, requirements)

    # 3. Running a simple Evolutionary Algorithm 
    pop = toolbox.population(n=50)  
    hof = tools.HallOfFame(1)       
    
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", lambda x: sum(y[0] for y in x) / len(x))
    stats.register("max", lambda x: max(y[0] for y in x))

    print("Starting Genetic Algorithm Evolution...")
    
    # Run the algorithm
    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=40, 
                                   stats=stats, halloffame=hof, verbose=True)

    # 4. Display Results
    best_ind = hof[0]
    print(f"\nBEST SCHEDULE FOUND (Score: {best_ind.fitness.values[0]}):")
    for i, sem in enumerate(best_ind):
        term = "Fall" if i % 2 == 0 else "Spring"
        print(f"Semester {i+1} ({term}): {sem}")