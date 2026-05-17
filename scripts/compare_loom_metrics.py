#!/usr/bin/env python3
"""Compare Loom metrics between source branch and project fingerprint."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Loom metrics")
    parser.add_argument("--branch-id", required=True)
    parser.add_argument("--project-slug", required=True)
    parser.add_argument("--base-dir", default="output/projects")
    args = parser.parse_args()

    heuristics_path = Path(args.base_dir) / args.project_slug / "style" / "heuristics.json"
    if not heuristics_path.exists():
        print(
            f"ERROR: {heuristics_path} not found. "
            f"Run: imitate-project fingerprint {args.project_slug}"
        )
        return 1

    with heuristics_path.open() as f:
        project_metrics: dict[str, object] = json.load(f)

    loom_metrics: dict[str, object] = {}
    try:
        result = subprocess.run(
            [".venv/bin/novel-analyzer", "loom-status", "--branch-id", args.branch_id],
            capture_output=True,
            text=True,
            timeout=30,
        )
        for line in result.stdout.splitlines():
            if "=" in line:
                k, _, v = line.partition("=")
                try:
                    loom_metrics[k.strip()] = float(v.strip())
                except ValueError:
                    loom_metrics[k.strip()] = v.strip()
    except Exception as e:
        print(f"WARNING: loom-status failed: {e}. Showing project metrics only.")

    print(f"\nLoom Phase 6 — Style Metrics Comparison")
    print(f"Branch: {args.branch_id} | Project: {args.project_slug}")
    print("-" * 70)
    print(f"{'Metric':<30} {'Project':<15} {'Branch':<15} {'Within 20%'}")
    print("-" * 70)

    all_ok = True
    for key, proj_val in project_metrics.items():
        if not isinstance(proj_val, (int, float)):
            print(f"{key:<30} {str(proj_val):<15}")
            continue

        branch_val = loom_metrics.get(key)
        if branch_val is None or not isinstance(branch_val, (int, float)):
            print(f"{key:<30} {proj_val:<15.3f} {'N/A':<15} ?")
            continue

        threshold = abs(proj_val) * 0.20
        within = abs(float(branch_val) - proj_val) <= threshold
        if not within:
            all_ok = False
        status = "✓" if within else "✗"
        print(f"{key:<30} {proj_val:<15.3f} {float(branch_val):<15.3f} {status}")

    print("-" * 70)
    print("PASS" if all_ok else "FAIL — some metrics outside ±20%")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
