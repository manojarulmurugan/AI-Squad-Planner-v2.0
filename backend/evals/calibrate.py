"""Calibration entry point; agreement maths is completed after the human handoff."""

from __future__ import annotations

import argparse

from evals.calibration import labels_path, load_labels
from evals.calibration import load_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true")
    parser.parse_args()
    if not labels_path().is_file():
        print("awaiting human labels")
        return
    data = load_labels()
    manifest = load_manifest()
    first_pass = sum(int(label.get("pass_index", 0)) == 1 for label in data["labels"])
    second_pass = sum(int(label.get("pass_index", 0)) == 2 for label in data["labels"])
    print(
        f"Human labels: pass 1 {first_pass}/{manifest['item_count']}; "
        f"consistency pass {second_pass}/3."
    )
    print("Agreement calculation is implemented in Phase 1 Session 3.")


if __name__ == "__main__":
    main()
