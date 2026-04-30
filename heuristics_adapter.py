from gpa_balancing import balance_reward, burnout_penalty
from workload_consistency import workload_consistency
from tuition_block import tuition_block
from scoring_heuristics import check_internship_readiness, check_freshman_buffer
from seniorload import senior_load_reduction
from prereqs import build_prereq_dict, calculate_prereq_points

HEURISTIC_SCALE = 100.0


def normalize_course_id(course_id: str) -> str:
    if not isinstance(course_id, str):
        return ""
    value = course_id.strip()
    if value.endswith("_U") or value.endswith("_C"):
        return value.rsplit("_", 1)[0]
    return value


def _as_numeric_score(value) -> float:
    if isinstance(value, tuple):
        if not value:
            return 0.0
        return float(value[0])
    if isinstance(value, list):
        if not value:
            return 0.0
        return float(value[0])
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def build_normalized_views(individual, G):
    schedule_base = []
    semester_dict = {}
    course_data = {}

    for course_id, node in G.nodes(data=True):
        difficulty_score = node.get("difficulty_Score", node.get("difficulty"))
        course_data[course_id] = {
            "name": node.get("name", course_id),
            "credit_hours": node.get("credit_hours", 0),
            "prereqs": node.get("prereqs", []),
            "availability": node.get("availability", []),
            "difficulty_Score": difficulty_score,
            "expected_gpa": node.get("expected_gpa", 4.0),
        }

    for sem_index, semester in enumerate(individual, start=1):
        sem_base = []
        for course_id in semester:
            base_id = normalize_course_id(course_id)
            if not base_id:
                continue
            sem_base.append(base_id)
        schedule_base.append(sem_base)
        semester_dict[sem_index] = sem_base

    return schedule_base, semester_dict, course_data


def compute_heuristics_breakdown(individual, G):
    schedule_base, semester_dict, course_data = build_normalized_views(individual, G)

    prereq_count = build_prereq_dict(course_data)

    burnout_penalty_score = _as_numeric_score(burnout_penalty(schedule_base, course_data))
    balance_reward_score = _as_numeric_score(balance_reward(schedule_base, course_data))
    workload_consistency_score = _as_numeric_score(workload_consistency(schedule_base, course_data))
    tuition_block_score = _as_numeric_score(tuition_block(individual, course_data))
    senior_load_score = _as_numeric_score(senior_load_reduction(schedule_base, course_data))
    prereq_score = _as_numeric_score(calculate_prereq_points(schedule_base, course_data, prereq_count, target_sem=6))

    internship_result = check_internship_readiness(semester_dict)
    freshman_result = check_freshman_buffer(semester_dict, course_data)
    internship_score = _as_numeric_score(internship_result.get("score", 0))
    freshman_score = _as_numeric_score(freshman_result.get("score", 0))

    components = {
        "burnout_penalty": burnout_penalty_score,
        "balance_reward": balance_reward_score,
        "workload_consistency": workload_consistency_score,
        "tuition_block": tuition_block_score,
        "senior_load_reduction": senior_load_score,
        "prereq_and_sequential": prereq_score,
        "internship_readiness": internship_score,
        "freshman_buffer": freshman_score,
    }

    scaled_components = {
        name: score * HEURISTIC_SCALE
        for name, score in components.items()
    }

    return {
        "raw_total": sum(components.values()),
        "total": sum(scaled_components.values()),
        "components": scaled_components,
        "raw_components": components,
        "internship": internship_result,
        "freshman": freshman_result,
    }


def compute_heuristics_delta(individual, G) -> float:
    return compute_heuristics_breakdown(individual, G)["total"]
