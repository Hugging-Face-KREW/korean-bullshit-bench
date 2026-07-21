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
        for field, value in row.items():
            if field == "is_control":
                assert isinstance(value, bool), f"{config}:{index}: invalid is_control"
            else:
                assert isinstance(value, str) and value.strip(), (
                    f"{config}:{index}: blank {field}"
                )
        ids.append(str(row["id"]))
        questions.append(str(row["question"]))

    assert len(ids) == len(set(ids)), f"{config}: duplicate IDs"
    assert len(questions) == len(set(questions)), f"{config}: duplicate questions"
    return rows


def main() -> None:
    translated = validate_config("translated_v2")
    native = validate_config("ko_native_v0_1")

    translated_domains = Counter(row["domain_group"] for row in translated)
    native_domains = Counter(row["domain"] for row in native)
    native_techniques = Counter(row["technique"] for row in native)
    native_difficulties = Counter(row["difficulty"] for row in native)

    assert sorted(translated_domains.values()) == [15, 15, 15, 15, 40]
    assert set(native_domains.values()) == {8}
    assert set(native_techniques.values()) == {6}
    assert set(native_difficulties) == {"easy", "medium", "hard"}

    all_ids = [str(row["id"]) for row in translated + native]
    assert len(all_ids) == len(set(all_ids)), "IDs collide across configs"

    print("Validation passed")
    print(f"  translated_v2: {len(translated)} questions")
    print(f"  ko_native_v0_1: {len(native)} questions")
    print(f"  total: {len(translated) + len(native)} questions")
    print(f"  native difficulty: {dict(sorted(native_difficulties.items()))}")


if __name__ == "__main__":
    main()
