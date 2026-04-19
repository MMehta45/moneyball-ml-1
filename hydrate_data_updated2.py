import json
import re
from pathlib import Path


REFERENCE_GPA = {
    "ECS 1100": 3.54,
    "CS 1200": 3.46,
    "CS 1436": 2.82,
    "CS 1337": 2.92,
    "CS 2305": 2.96,
    "CS 2336": 3.18,
    "GOVT 2305": 3.14,
    "MATH 2418": 2.58,
    "RHET 1302": 3.23,
    "PHYS 2125": 3.76,
    "PHYS 2126": 3.77,
    "PHYS 2325": 3.16,
    "PHYS 2326": 3.05,
    "MATH 2413": 2.33,
    "MATH 2414": 2.41,
    "MATH 2417": 2.36,
    "MATH 2419": 2.52,
    "CS 3162": 3.63,
    "CS 3341": 2.87,
    "CS 3345": 3.25,
    "CS 3354": 3.41,
    "CS 3377": 3.20,
    "ECS 2390": 3.46,
    "CS 4141": 3.71,
    "Language, Philosophy, and Culture": 3.10,
    "Creative Arts": 3.38,
    "American History": 3.21,
    "Social and Behavioral Sciences": 3.19,
    "CS 4337": 3.096,
    "CS 4341": 3.154,
    "CS 4347": 3.341,
    "CS 4348": 2.988,
    "CS 4384": 3.124,
    "CS 4385": None,
    "CS 4314": 3.030,
    "CS 4315": 3.303,
    "CS 4332": 3.763,
    "CS 4334": 2.826,
    "CS 4336": 3.243,
    "CS 4339": None,
    "CS 4352": 3.757,
    "CS 4361": 3.228,
    "CS 4365": 3.107,
    "CS 4375": 3.244,
    "CS 4376": 3.038,
    "CS 4386": 2.795,
    "CS 4389": 3.299,
    "CS 4390": 3.051,
    "CS 4391": 3.240,
    "CS 4392": 3.187,
    "CS 4393": 2.954,
    "CS 4394": 3.333,
    "CS 4395": 3.423,
    "CS 4396": 3.166,
    "CS 4397": 3.207,
    "CS 4398": 3.128,
    "CS 4399": None,
    "CS 4359": 3.822,
    "EE 4325": 3.076,
    "SE 4351": 3.299,
    "SE 4352": 3.301,
    "SE 4367": 2.936,
    "SE 4381": 3.267,
}


CATEGORY_GPA = {
    "Language, Philosophy, and Culture": 3.10,
    "Creative Arts": 3.38,
    "American History": 3.21,
    "Social and Behavioral Sciences": 3.19,
}


CATEGORY_COURSES = {
    "Language, Philosophy, and Culture": {
        "AMS2300", "AMS2341", "ATCM2300", "ATCM2322", "ATCM2325", "COMM1320",
        "COMM2314", "FILM1303", "HIST2340", "HIST2341", "HIST2350", "HIST2360",
        "HIST2370", "HUMA1301", "LIT1301", "LIT2322", "LIT2329", "LIT2331",
        "PHIL1301", "PHIL1305", "PHIL1306", "PHIL2316", "PHIL2317", "RELS1325",
    },
    "Creative Arts": {
        "AHST1303", "AHST1304", "AHST2331", "ARTS1301", "ATCM2321", "CRWT2301",
        "DANC1305", "DANC1310", "FILM2332", "LIT1311", "LIT1315", "MUSI1306",
        "MUSI2321", "MUSI2322", "PHIL1307", "THEA1310",
    },
    "American History": {
        "HIST1301", "HIST1302", "HIST2301", "HIST2330", "HIST2381", "HIST2384",
    },
    "Social and Behavioral Sciences": {
        "BA1310", "BA1320", "CLDP2314", "CRIM1301", "CRIM1307", "ECON2301",
        "ECON2302", "GEOG2303", "GST2300", "LIT1331", "PA2325", "PSY2301",
        "PSY2314", "SOC1301", "SOC1306", "SOC2300",
    },
}


def canonical(code: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", code.upper())


def spaced_to_canonical(code: str) -> str:
    return canonical(code)


def canonical_to_spaced(code: str) -> str | None:
    match = re.fullmatch(r"([A-Z]+)(\d{4})", code)
    if not match:
        return None
    return f"{match.group(1)} {match.group(2)}"


def candidate_course_codes(raw_key: str) -> list[str]:
    stripped = re.sub(r"\(.*?\)", "", raw_key)
    parts = [part for part in re.split(r"/", stripped) if part]

    candidates: list[str] = []
    for part in parts:
        token = canonical(part)
        if not token:
            continue

        full = re.fullmatch(r"([A-Z]+)(\d{4})", token)
        if full:
            candidates.append(token)
            continue

        short = re.fullmatch(r"(\d{4})", token)
        if short and candidates:
            prev_dept = re.fullmatch(r"([A-Z]+)(\d{4})", candidates[-1])
            if prev_dept:
                candidates.append(f"{prev_dept.group(1)}{short.group(1)}")

    seen = set()
    ordered = []
    for code in candidates:
        if code not in seen:
            seen.add(code)
            ordered.append(code)
    return ordered


def category_for_code(code: str) -> str | None:
    adjusted = code
    if adjusted.startswith("AHS"):
        adjusted = "AHST" + adjusted[3:]

    for category, course_set in CATEGORY_COURSES.items():
        if adjusted in course_set:
            return category
    return None


def build_reference_index() -> dict[str, float]:
    indexed: dict[str, float] = {}
    for k, v in REFERENCE_GPA.items():
        if v is None:
            continue
        key = spaced_to_canonical(k)
        if re.fullmatch(r"[A-Z]+\d{4}", key):
            indexed[key] = float(v)
    return indexed


def compute_difficulty(expected_gpa: float) -> float:
    return round(4.0 - expected_gpa, 3)


def hydrate(master_path: Path) -> tuple[int, int]:
    with master_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    ref_index = build_reference_index()
    hydrated_expected = 0
    hydrated_difficulty = 0

    for raw_key, record in data.items():
        expected = record.get("expected_gpa")
        diff_lower = record.get("difficulty_score")
        diff_upper = record.get("difficulty_Score")

        resolved_expected = expected

        if resolved_expected is None:
            for code in candidate_course_codes(raw_key):
                if code in ref_index:
                    resolved_expected = ref_index[code]
                    break

            if resolved_expected is None:
                for code in candidate_course_codes(raw_key):
                    category = category_for_code(code)
                    if category:
                        resolved_expected = CATEGORY_GPA[category]
                        break

            if resolved_expected is not None:
                record["expected_gpa"] = round(float(resolved_expected), 3)
                hydrated_expected += 1

        resolved_expected = record.get("expected_gpa")
        if resolved_expected is not None:
            target_difficulty = compute_difficulty(float(resolved_expected))

            if diff_lower is None:
                record["difficulty_score"] = target_difficulty
                hydrated_difficulty += 1
            if "difficulty_Score" in record and diff_upper is None:
                record["difficulty_Score"] = target_difficulty

    with master_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return hydrated_expected, hydrated_difficulty


def main() -> None:
    target = Path("data_updated2.json")
    expected_count, difficulty_count = hydrate(target)
    print(f"Hydrated expected_gpa fields: {expected_count}")
    print(f"Hydrated difficulty_score fields: {difficulty_count}")


if __name__ == "__main__":
    main()
