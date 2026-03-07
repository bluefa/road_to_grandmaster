#!/usr/bin/env python3
"""Lookup AtCoder problem difficulty from the vendored local dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATASET = REPO_ROOT / "data" / "atcoder" / "problem-models.json"


def load_models(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lookup AtCoder difficulty from the local vendored problem-models.json"
    )
    parser.add_argument("problem_id", help="AtCoder task id such as abc436_g")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help="Path to the vendored problem-models.json file",
    )
    parser.add_argument(
        "--value-only",
        action="store_true",
        help="Print only the numeric difficulty or null",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    dataset_path: Path = args.dataset.resolve()
    if not dataset_path.exists():
        raise SystemExit(f"dataset not found: {dataset_path}")

    models = load_models(dataset_path)
    model = models.get(args.problem_id)
    difficulty = None if model is None else model.get("difficulty")

    if args.value_only:
        print("null" if difficulty is None else difficulty)
        return 0

    result = {
        "problem_id": args.problem_id,
        "found": model is not None,
        "difficulty": difficulty,
        "source": "kenkoooo-local",
        "dataset_path": str(dataset_path),
    }
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
