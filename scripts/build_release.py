#!/usr/bin/env python3
"""Build release JSONL files from exported editorial CSV files."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


DOMAIN_CODES = {
    "software_ai": "sai",
    "startup_product": "sp",
    "finance_business": "fb",
    "legal_labor_tax": "llt",
    "medical_health": "mh",
    "public_education_career": "pec",
}

TECHNIQUE_CODES = {
    "fabricated_framework": "ff",
    "fabricated_metric": "fm",
    "misapplied_mechanism": "mm",
    "cross_domain_stitching": "cds",
    "false_precision": "fp",
    "reified_metaphor": "rm",
    "nested_nonsense": "nn",
    "temporal_category_error": "tce",
}

TRANSLATED_FIELDS = (
    "id",
    "question",
    "nonsensical_element",
    "domain",
    "domain_group",
    "difficulty",
    "difficulty_label",
    "technique",
    "is_control",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def flatten_original(path: Path) -> dict[str, dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    questions = [
        question
        for technique_group in payload["techniques"]
        for question in technique_group["questions"]
    ]
    return {str(question["id"]): question for question in questions}


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_translated(
    translated_csv: Path, original_json: Path
) -> list[dict[str, object]]:
    sheet_rows = read_csv(translated_csv)
    original_by_id = flatten_original(original_json)
    sheet_ids = {row["id"] for row in sheet_rows}

    if sheet_ids != set(original_by_id):
        missing = sorted(set(original_by_id) - sheet_ids)
        extra = sorted(sheet_ids - set(original_by_id))
        raise ValueError(f"Original ID mismatch. missing={missing}, extra={extra}")

    output = []
    for row in sheet_rows:
        original = original_by_id[row["id"]]
        item = {field: original[field] for field in TRANSLATED_FIELDS}
        item["question"] = row["question_ko"].strip()
        item["nonsensical_element"] = row["nonsensical_element_ko"].strip()
        output.append(item)
    return output


def build_native(
    native_csv: Path, keep_creator: str | None = None
) -> list[dict[str, object]]:
    counters: defaultdict[tuple[str, str], int] = defaultdict(int)
    output = []

    for row in read_csv(native_csv):
        domain = row["domain"].strip()
        technique = row["technique"].strip()
        if domain not in DOMAIN_CODES or technique not in TECHNIQUE_CODES:
            raise ValueError(f"Unknown taxonomy value: {domain=}, {technique=}")

        key = (domain, technique)
        counters[key] += 1
        item_id = (
            f"{DOMAIN_CODES[domain]}_{TECHNIQUE_CODES[technique]}_"
            f"{counters[key]:02d}"
        )
        if keep_creator and row["creator"].strip() != keep_creator:
            output.append(
                {
                    "id": item_id,
                    "domain": None,
                    "technique": None,
                    "difficulty": None,
                    "question": None,
                    "nonsensical_element": None,
                    "is_control": None,
                }
            )
            continue

        output.append(
            {
                "id": item_id,
                "domain": domain,
                "technique": technique,
                "difficulty": row["difficulty"].strip(),
                "question": row["question_ko"].strip(),
                "nonsensical_element": row["nonsensical_element_ko"].strip(),
                "is_control": False,
            }
        )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--translated-csv", type=Path, required=True)
    parser.add_argument("--native-csv", type=Path, required=True)
    parser.add_argument("--original-json", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("data"))
    parser.add_argument(
        "--keep-native-creator",
        help="Keep only this creator's native rows and emit null placeholders for others",
    )
    args = parser.parse_args()

    translated = build_translated(args.translated_csv, args.original_json)
    native = build_native(args.native_csv, args.keep_native_creator)

    write_jsonl(args.output_root / "translated_v2" / "test.jsonl", translated)
    write_jsonl(args.output_root / "ko_native_v0_1" / "test.jsonl", native)
    print(f"Wrote {len(translated)} translated and {len(native)} native questions.")


if __name__ == "__main__":
    main()
