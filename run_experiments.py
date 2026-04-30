import os
import time
import json
import random
from statistics import mean, median

from deap import base, tools, algorithms, creator

from create_graph import load_data_from_json, create_graph
from create_schedule import generate_individual
from evaluate import evaluate
from heuristics_adapter import compute_heuristics_breakdown


def total_hours(individual, G):
    return sum(G.nodes[course.split('_')[0]]['credit_hours'] for semester in individual for course in semester)


def semester_hours(individual, G):
    return [
        sum(G.nodes[course.split('_')[0]]['credit_hours'] for course in semester)
        for semester in individual
    ]


def make_toolbox(G, requirements, mut_indpb=0.20, tournsize=5):
    toolbox = base.Toolbox()
    # Individual generator uses generate_individual with the graph + requirements
    # Use the same Individual type created by the project (creator.Individual)
    toolbox.register("individual", tools.initIterate, creator.Individual, lambda: generate_individual(G, requirements=requirements))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", lambda ind: evaluate(ind, G, requirements))
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=mut_indpb)
    toolbox.register("select", tools.selTournament, tournsize=tournsize)
    return toolbox


def run_single(seed, G, requirements, pop_size=200, ngen=300, cxpb=0.8, mutpb=0.4):
    random.seed(seed)
    toolbox = make_toolbox(G, requirements)

    pop = toolbox.population(n=pop_size)
    pop[0] = creator.Individual(generate_individual(G, requirements=requirements, seed_mode=True))
    hof = tools.HallOfFame(5)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", lambda x: sum(y[0] for y in x) / len(x))
    stats.register("max", lambda x: max(y[0] for y in x))

    t0 = time.time()
    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mutpb, ngen=ngen,
                                   stats=stats, halloffame=hof, verbose=False)
    t1 = time.time()
    runtime = t1 - t0

    best = hof[0]
    best_score = best.fitness.values[0]
    confirmed_best_score = evaluate(best, G, requirements)[0]

    # convert hof to plain lists for JSON
    hof_plain = []
    hof_details = []
    for indiv in hof:
        schedule = [list(sem) for sem in indiv]
        score = evaluate(indiv, G, requirements)[0]
        hof_plain.append(schedule)
        hof_details.append({
            "score": score,
            "fitness_score": indiv.fitness.values[0],
            "total_hours": total_hours(indiv, G),
            "semester_hours": semester_hours(indiv, G),
            "heuristics": compute_heuristics_breakdown(indiv, G),
            "schedule": schedule,
        })

    return {
        "seed": seed,
        "best_score": best_score,
        "confirmed_best_score": confirmed_best_score,
        "best_total_hours": total_hours(best, G),
        "best_semester_hours": semester_hours(best, G),
        "best_heuristics": compute_heuristics_breakdown(best, G),
        "best_schedule": [list(sem) for sem in best],
        "runtime": runtime,
        "hof": hof_plain,
        "hof_details": hof_details,
    }


def main():
    raw = load_data_from_json('data_updated2.json')
    with open('requirements.json') as f:
        requirements = json.load(f)
    G = create_graph(raw)

    # Experiment parameters — adjust if you want longer runs
    runs = 10
    pop_size = 200
    ngen = 300
    cxpb = 0.8
    mutpb = 0.4

    results = []
    os.makedirs('results', exist_ok=True)

    for seed in range(1, runs + 1):
        print(f"Running seed={seed}...")
        res = run_single(seed, G, requirements, pop_size=pop_size, ngen=ngen, cxpb=cxpb, mutpb=mutpb)
        results.append(res)
        # write hof for this run
        fname = f"results/best_schedules_seed_{seed}.json"
        with open(fname, 'w') as f:
            json.dump(res, f, indent=2)
        print(f"  seed={seed} done — best={res['best_score']:.2f}, runtime={res['runtime']:.1f}s")

    scores = [r['best_score'] for r in results]
    runtimes = [r['runtime'] for r in results]

    summary = {
        'runs': runs,
        'pop_size': pop_size,
        'ngen': ngen,
        'cxpb': cxpb,
        'mutpb': mutpb,
        'best_overall': max(scores),
        'median_best': median(scores),
        'mean_best': mean(scores),
        'best_seed': next(r['seed'] for r in results if r['best_score'] == max(scores)),
        'runtimes': runtimes,
        'mean_runtime': mean(runtimes),
    }

    with open('results/experiment_summary.json', 'w') as f:
        json.dump({'summary': summary, 'results': results}, f, indent=2)

    print('\nExperiment complete:')
    print(f"  runs={runs}, pop={pop_size}, ngen={ngen}")
    print(f"  best_overall={summary['best_overall']:.2f} (seed {summary['best_seed']})")
    print(f"  median_best={summary['median_best']:.2f}, mean_best={summary['mean_best']:.2f}")
    print(f"  mean_runtime={summary['mean_runtime']:.1f}s")


if __name__ == '__main__':
    main()
