#!/usr/bin/env python3
"""Validate Korean BullshitBench release files."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "translated_v2": ROOT / "data" / "translated_v2" / "test.jsonl",
    "ko_native_v0_1": ROOT / "data" / "ko_native_v0_1" / "test.jsonl",
}

EXPECTED_COUNTS = {
    "translated_v2": 100,
    "ko_native_v0_1": 48,
}

EXPECTED_FIELDS = {
    "translated_v2": {
        "id",
        "question",
        "nonsensical_element",
        "domain",
        "domain_group",
        "difficulty",
        "difficulty_label",
        "technique",
        "is_control",
    },
    "ko_native_v0_1": {
        "id",
        "domain",
        "technique",
        "difficulty",
        "question",
        "nonsensical_element",
        "is_control",
    },
}

NATIVE_DOMAINS = {
    "software_ai",
    "startup_product",
    "finance_business",
    "legal_labor_tax",
    "medical_health",
    "public_education_career",
}

NATIVE_TECHNIQUES = {
    "fabricated_framework",
    "fabricated_metric",
    "misapplied_mechanism",
    "cross_domain_stitching",
    "false_precision",
    "reified_metaphor",
    "nested_nonsense",
    "temporal_category_error",
}


def read_jsonl(path: Path) -> list[dict[str, object]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from error
    return rows


def validate_config(config: str) -> list[dict[str, object]]:
    rows = read_jsonl(FILES[config])
    assert len(rows) == EXPECTED_COUNTS[config], (
        f"{config}: expected {EXPECTED_COUNTS[config]} rows, found {len(rows)}"
    )

    ids = []
    questions = []
    for index, row in enumerate(rows, start=1):
        assert set(row) == EXPECTED_FIELDS[config], (
            f"{config}:{index}: unexpected fields {sorted(set(row))}"
        )
        if config == "ko_native_v0_1":
            values = [value for field, value in row.items() if field != "id"]
            placeholder = all(value is None for value in values)
            populated = all(value is not None for value in values)
            assert placeholder or populated, f"{config}:{index}: partially filled row"
        else:
            populated = True

        assert isinstance(row["id"], str) and row["id"].strip(), (
            f"{config}:{index}: blank id"
        )
        if populated:
            for field, value in row.items():
                if field == "is_control":
                    assert isinstance(value, bool), (
                        f"{config}:{index}: invalid is_control"
                    )
                else:
                    assert isinstance(value, str) and value.strip(), (
                        f"{config}:{index}: blank {field}"
                    )
        ids.append(str(row["id"]))
        if row["question"] is not None:
            questions.append(str(row["question"]))

    assert len(ids) == len(set(ids)), f"{config}: duplicate IDs"
    assert len(questions) == len(set(questions)), f"{config}: duplicate questions"
    return rows


def main() -> None:
    translated = validate_config("translated_v2")
    native = validate_config("ko_native_v0_1")

    translated_domains = Counter(row["domain_group"] for row in translated)
    populated_native = [row for row in native if row["question"] is not None]
    native_domains = Counter(row["domain"] for row in populated_native)
    native_techniques = Counter(row["technique"] for row in populated_native)
    native_difficulties = Counter(row["difficulty"] for row in populated_native)

    assert sorted(translated_domains.values()) == [15, 15, 15, 15, 40]
    assert set(native_domains) <= NATIVE_DOMAINS
    assert set(native_techniques) <= NATIVE_TECHNIQUES
    assert set(native_difficulties) <= {"easy", "medium", "hard"}

    all_ids = [str(row["id"]) for row in translated + native]
    assert len(all_ids) == len(set(all_ids)), "IDs collide across configs"

    print("Validation passed")
    print(f"  translated_v2: {len(translated)} questions")
    print(
        f"  ko_native_v0_1: {len(populated_native)} populated, "
        f"{len(native) - len(populated_native)} placeholders"
    )
    print(f"  total rows: {len(translated) + len(native)}")
    print(f"  native difficulty: {dict(sorted(native_difficulties.items()))}")


if __name__ == "__main__":
    main()
