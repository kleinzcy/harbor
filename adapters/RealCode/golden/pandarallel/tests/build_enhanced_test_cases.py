#!/usr/bin/env python3
"""
Merge tests/test_cases into tests/enhanced_test_cases and append supplemental cases.
Goldens for new numeric cases are computed with the same serial recipe as generate_expected.py.
"""
from __future__ import annotations

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, ROOT)
sys.path.insert(0, SCRIPT_DIR)

from generate_expected import ExpectedOutputGenerator  # noqa: E402

SRC_DIR = os.path.join(SCRIPT_DIR, "test_cases")
DST_DIR = os.path.join(SCRIPT_DIR, "enhanced_test_cases")

# Supplemental cases: only "input" required; expected_output filled by generator (except exceptions).
SUPPLEMENTS: dict[str, list[dict]] = {
    "feature1_core_operations.json": [
        {
            "input": {
                "operation": "dataframe_apply",
                "axis": 0,
                "df_size": 1,
                "func": "lambda x: x.sum(numeric_only=True)",
            }
        },
        {
            "input": {
                "operation": "dataframe_apply",
                "axis": 1,
                "df_size": 1,
                "func": "lambda x: x.sum(numeric_only=True)",
            }
        },
        {
            "input": {
                "operation": "series_apply",
                "df_size": 1,
                "func": "lambda x: x**2",
            }
        },
        {
            "input": {
                "operation": "dataframe_applymap",
                "df_size": 5,
                "func": "lambda x: x * 3",
            }
        },
        {
            "input": {
                "operation": "dataframe_apply",
                "axis": 0,
                "df_size": 300,
                "func": "lambda x: x.mean(numeric_only=True)",
            }
        },
    ],
    "feature2_1_groupby.json": [
        {
            "input": {
                "operation": "groupby_apply",
                "group_cols": ["a"],
                "df_size": 45,
                "func": "lambda g: g.sum(numeric_only=True)",
            }
        },
        {
            "input": {
                "operation": "groupby_apply",
                "group_cols": ["a", "b"],
                "df_size": 90,
                "func": "lambda g: g.mean(numeric_only=True)",
            }
        },
    ],
    "feature2_2_rolling.json": [
        {
            "input": {
                "operation": "series_rolling",
                "window": 2,
                "df_size": 85,
                "func": "lambda w: w.sum()",
            }
        },
        {
            "input": {
                "operation": "series_rolling",
                "window": 7,
                "df_size": 110,
                "func": "lambda w: w.mean()",
            }
        },
        {
            "input": {
                "operation": "groupby_rolling",
                "group_col": "group",
                "window": 3,
                "df_size": 95,
                "func": "lambda w: w.sum(numeric_only=True)",
            }
        },
    ],
    "feature2_3_expanding.json": [
        {
            "input": {
                "operation": "series_expanding",
                "df_size": 18,
                "func": "lambda w: w.sum()",
            }
        },
        {
            "input": {
                "operation": "groupby_expanding",
                "group_col": "group",
                "df_size": 55,
                "func": "lambda w: w.max(numeric_only=True)",
            }
        },
    ],
    "feature3_progress_bar.json": [
        {
            "input": {
                "progress_bar": True,
                "operation": "dataframe_apply",
                "df_size": 1,
            }
        },
        {
            "input": {
                "progress_bar": False,
                "operation": "series_map",
                "df_size": 25,
            }
        },
    ],
    "feature4_2_memory_fs.json": [
        {
            "input": {
                "use_memory_fs": None,
                "operation": "dataframe_apply",
                "df_size": 35,
            }
        },
        {
            "input": {
                "use_memory_fs": True,
                "operation": "series_apply",
                "df_size": 42,
                "func": "lambda x: x + 10",
            }
        },
    ],
    "feature4_3_configuration.json": [
        {
            "input": {
                "nb_workers": 4,
                "progress_bar": False,
                "verbose": 0,
                "use_memory_fs": None,
            }
        },
    ],
    "feature5_exception_handling.json": [
        {
            "input": {
                "operation": "dataframe_apply",
                "axis": 0,
                "df_size": 20,
                "func": "lambda x: int(str(x.name).replace('col','')) / 0",
            },
            "expected_output": "ZeroDivisionError",
        },
        {
            "input": {
                "operation": "series_apply",
                "df_size": 15,
                "func": "lambda x: int('not_a_number')",
            },
            "expected_output": "ValueError",
        },
    ],
}


def _should_skip_expected_fill(expected: str) -> bool:
    if expected in ("ZeroDivisionError", "AttributeError", "ValueError"):
        return True
    if isinstance(expected, str) and expected.startswith(">="):
        return True
    return False


def main() -> None:
    os.makedirs(DST_DIR, exist_ok=True)
    gen = ExpectedOutputGenerator()

    for name in sorted(os.listdir(SRC_DIR)):
        if not name.endswith(".json"):
            continue
        src_path = os.path.join(SRC_DIR, name)
        dst_path = os.path.join(DST_DIR, name)
        with open(src_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        extra = SUPPLEMENTS.get(name, [])
        base_desc = data.get("description", "")
        if extra:
            data["description"] = (
                base_desc
                + " [Enhanced: added boundary/window/IPC/config/exception-diversity cases.]"
            )
        for case in extra:
            if "expected_output" not in case:
                case["expected_output"] = ""
            exp = case.get("expected_output", "")
            if not _should_skip_expected_fill(exp):
                case["expected_output"] = gen.compute_expected_output(case)
            data.setdefault("cases", []).append(case)

        with open(dst_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            f.write("\n")
        print(f"Wrote {dst_path} ({len(data['cases'])} cases)")


if __name__ == "__main__":
    main()
