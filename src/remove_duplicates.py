from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def normalized_hash(text: str) -> str:
    normalized = " ".join(str(text).lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove exact duplicate job postings."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    seen: set[str] = set()
    retained: list[dict] = []

    with input_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            record = json.loads(line)
            description = record.get("description", "")

            if not description:
                print(f"Skipping line {line_number}: empty description")
                continue

            text_hash = normalized_hash(description)

            if text_hash in seen:
                continue

            seen.add(text_hash)
            record["text_hash"] = text_hash
            retained.append(record)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        for record in retained:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Retained {len(retained)} unique postings")


if __name__ == "__main__":
    main()
