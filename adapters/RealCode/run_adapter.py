from __future__ import annotations

import argparse
from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from adapter import RealCodeAdapter  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert RealCode dataset into Harbor task directories."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./datasets/realcode"),
        help="Output directory for generated Harbor tasks.",
    )
    parser.add_argument(
        "--task-ids",
        type=str,
        default=None,
        help="Comma-separated source task IDs. If omitted, converts all tasks.",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="realcode_",
        help="Prefix for generated local Harbor task IDs.",
    )
    args = parser.parse_args()

    adapter = RealCodeAdapter(task_dir=args.output_dir)

    if args.task_ids:
        task_ids = [task_id.strip() for task_id in args.task_ids.split(",") if task_id]
    else:
        task_ids = adapter.list_available_tasks()

    if not task_ids:
        print("No tasks selected.")
        return

    args.output_dir.mkdir(parents=True, exist_ok=True)
    success = 0
    for task_id in task_ids:
        local_task_id = f"{args.prefix}{task_id}"
        print(f"Generating {task_id} -> {local_task_id}")
        output_dir = adapter.generate_task(task_id=task_id, local_task_id=local_task_id)
        print(f"Created: {output_dir}")
        success += 1

    print(f"Done. Generated {success} task(s) in {args.output_dir}")


if __name__ == "__main__":
    main()
