from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.common import load_json


def classify_domain(
    text: str,
    domain_rules: dict[str, list[str]],
) -> str:
    normalized = str(text).lower()
    scores = {
        domain: sum(keyword in normalized for keyword in keywords)
        for domain, keywords in domain_rules.items()
    }

    best_domain = max(scores, key=scores.get)

    if scores[best_domain] == 0:
        return "other"

    return best_domain


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Assign broad job domains using documented rules."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rules = load_json(args.config)

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with (
        input_path.open("r", encoding="utf-8") as source,
        output_path.open("w", encoding="utf-8") as destination,
    ):
        for line in source:
            if not line.strip():
                continue

            record = json.loads(line)
            combined_text = " ".join(
                [
                    str(record.get("title", "")),
                    str(record.get("description", "")),
                ]
            )
            record["role_domain"] = classify_domain(
                combined_text,
                rules,
            )
            destination.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )


if __name__ == "__main__":
    main()
