import argparse
import math
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import config


def draw_sensitivity_percent_change(max_pressure: float | None = None) -> pathlib.Path:
    if max_pressure is not None and (
        not math.isfinite(max_pressure) or max_pressure <= 0
    ):
        raise ValueError("max_pressure must be a finite positive number")

    results_dir = parent_dir / config.RESULTS_DIR
    sensitivity_dir = results_dir / "sensitivity"
    csv_paths = sorted(sensitivity_dir.glob("*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found in {sensitivity_dir}")

    fig, ax = plt.subplots(figsize=(14, 8))

    for csv_path in csv_paths:
        df = pd.read_csv(csv_path)
        missing_columns = {"pressure", "perf"} - set(df.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"{csv_path} is missing required column(s): {missing}")
        if len(df) < 2:
            raise ValueError(f"{csv_path} must contain at least two data rows")

        df["pressure"] = pd.to_numeric(df["pressure"], errors="raise")
        df["perf"] = pd.to_numeric(df["perf"], errors="raise")
        df = df.sort_values("pressure")
        pressure = df["pressure"].to_numpy()
        perf = df["perf"].to_numpy()

        if not np.isfinite(pressure).all() or not np.isfinite(perf).all():
            raise ValueError(f"{csv_path} contains non-finite pressure or perf values")
        if np.any(np.diff(pressure) <= 0):
            raise ValueError(f"{csv_path} must have unique pressure values")
        if np.any(perf[:-1] == 0):
            raise ValueError(
                f"{csv_path} has a zero perf value used as a comparison baseline"
            )

        percent_change = np.diff(perf) / perf[:-1] * 100
        pressure_steps = pressure[1:] / 32
        if max_pressure is not None:
            visible_points = pressure_steps <= max_pressure
            pressure_steps = pressure_steps[visible_points]
            percent_change = percent_change[visible_points]

        name_parts = csv_path.stem.split("_")
        ax.plot(
            pressure_steps,
            percent_change,
            marker="o",
            markersize=3,
            linewidth=1,
            label=name_parts[1] if len(name_parts) >= 3 else csv_path.stem,
        )

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Pressure (32-unit steps)")
    ax.set_ylabel("Performance change from previous step (%)")
    ax.set_title("Step-to-step performance change by workload")
    if max_pressure is not None:
        ax.set_xlim(left=0, right=max_pressure)
    ax.grid(True, alpha=0.3)
    ax.legend(
        title="Workload",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        fontsize="small",
    )
    fig.tight_layout()

    output_path = results_dir / "sensitivity_percent_change.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot step-to-step performance changes from sensitivity CSVs."
    )
    parser.add_argument(
        "--max-pressure",
        type=float,
        help="Maximum plotted pressure in 32-unit steps (e.g. 4 shows up to pressure 128).",
    )
    args = parser.parse_args()
    print(draw_sensitivity_percent_change(max_pressure=args.max_pressure))
