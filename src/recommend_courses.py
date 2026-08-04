from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rank SFU CMPT courses against a skill-gap vector."
    )
    parser.add_argument("--gap-file", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    raise SystemExit(
        "Course recommendation is not implemented yet. "
        "Use the same fitted feature space for the gap and course vectors. "
        f"Requested top-k: {args.top_k}."
    )


if __name__ == "__main__":
    main()
