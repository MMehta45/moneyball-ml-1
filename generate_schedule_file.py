import json
import random
import time
from pathlib import Path

from create_graph import load_data_from_json, create_graph
from run_experiments import run_single


ROOT = Path(__file__).resolve().parent
SCHEDULE_PATH = ROOT / "schedule.json"
FALLBACK_PATH = ROOT / "fallback.json"
DATA_PATH = ROOT / "data_updated2.json"
REQUIREMENTS_PATH = ROOT / "requirements.json"


def adapt_schedule(individual):
    adapted = []
    for index, semester in enumerate(individual, start=1):
        adapted.append(
            {
                "semester": index,
                "term": "Fall" if index % 2 == 1 else "Spring",
                "courses": semester,
            }
        )
    return adapted


def main():
    raw = load_data_from_json(str(DATA_PATH))
    with REQUIREMENTS_PATH.open() as requirements_file:
        requirements = json.load(requirements_file)
    graph = create_graph(raw)

    # One moderate DEAP run keeps the UI responsive enough for local use.
    seed = int(time.time())
    result = run_single(seed, graph, requirements, pop_size=120, ngen=120, cxpb=0.8, mutpb=0.35)

    if result["confirmed_best_score"] < 0:
        with FALLBACK_PATH.open() as fallback_file:
            schedule_payload = json.load(fallback_file)
        source = "fallback"
        score = result["confirmed_best_score"]
    else:
        schedule_payload = adapt_schedule(result["best_schedule"])
        source = "deap"
        score = result["confirmed_best_score"]

    with SCHEDULE_PATH.open("w") as schedule_file:
        json.dump(schedule_payload, schedule_file, indent=2)

    print(
        json.dumps(
            {
                "source": source,
                "score": score,
                "schedule_path": str(SCHEDULE_PATH),
            }
        )
    )


if __name__ == "__main__":
    main()
