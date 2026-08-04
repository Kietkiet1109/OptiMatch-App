from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect publicly accessible job postings."
    )
    parser.add_argument("--source", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    raise SystemExit(
        "Job collection is not implemented yet. "
        f"Implement a permitted collector for {args.source!r}. "
        "Do not circumvent authentication, CAPTCHAs, or access controls."
    )


if __name__ == "__main__":
    main()
