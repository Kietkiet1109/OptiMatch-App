from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect publicly available SFU CMPT course descriptions."
    )
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    raise SystemExit(
        "Course collection is not implemented yet. "
        f"Write validated records to {args.output!r}."
    )


if __name__ == "__main__":
    main()
