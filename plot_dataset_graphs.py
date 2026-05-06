"""
Generate EDA graphs for Smart Crop Advisor dataset.

Reads:
  - data/crop_data.csv (preferred)
  - falls back to data/Crop_recommendation.csv if crop_data.csv is missing

Saves PNGs to:
  - plots/

Run:
  python plot_dataset_graphs.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parent
PREFERRED_DATASET = PROJECT_ROOT / "data" / "crop_data.csv"
FALLBACK_DATASET = PROJECT_ROOT / "data" / "Crop_recommendation.csv"
PLOTS_DIR = PROJECT_ROOT / "plots"

TOP_N_LABELS = 10
SAMPLE_SIZE_SCATTER = 1200


def load_dataset() -> tuple[pd.DataFrame, str]:
    if PREFERRED_DATASET.exists():
        return pd.read_csv(PREFERRED_DATASET), str(PREFERRED_DATASET)
    if FALLBACK_DATASET.exists():
        return pd.read_csv(FALLBACK_DATASET), str(FALLBACK_DATASET)
    raise FileNotFoundError(
        "No dataset found. Expected one of:\n"
        f"- {PREFERRED_DATASET}\n"
        f"- {FALLBACK_DATASET}\n"
    )


def save_fig(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()


def add_note_box(ax, text: str) -> None:
    """
    Draw a small note box inside the plot area (top-right).
    """
    ax.text(
        0.99,
        0.99,
        text,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=10,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.95},
    )


def annotate_barh(ax, total: int) -> None:
    """
    Adds 'count (pct%)' labels to horizontal bars.
    """
    for patch in ax.patches:
        width = patch.get_width()
        if width <= 0:
            continue
        pct = 100.0 * (width / max(total, 1))
        ax.text(
            width + (0.01 * ax.get_xlim()[1]),
            patch.get_y() + patch.get_height() / 2,
            f"{int(width)}  ({pct:.1f}%)",
            va="center",
            fontsize=10,
            color="#0f172a",
        )


def annotate_bar(ax, total: int) -> None:
    """
    Adds 'count (pct%)' labels above vertical bars.
    """
    for patch in ax.patches:
        height = patch.get_height()
        if height <= 0:
            continue
        pct = 100.0 * (height / max(total, 1))
        ax.text(
            patch.get_x() + patch.get_width() / 2,
            height + (0.01 * ax.get_ylim()[1]),
            f"{int(height)}\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=10,
            color="#0f172a",
        )


def main() -> None:
    sns.set_theme(style="whitegrid", context="talk")
    df, source = load_dataset()

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Crop label distribution (Top N) with count + percentage labels
    if "label" in df.columns:
        labels = df["label"].astype(str)
        vc = labels.value_counts().head(TOP_N_LABELS)
        total = int(vc.sum())

        plt.figure(figsize=(12, 7))
        ax = sns.barplot(
            x=vc.values,
            y=vc.index,
            hue=vc.index,
            legend=False,
            palette="viridis",
        )
        ax.set_title(f"Crop distribution (Top {TOP_N_LABELS})")
        ax.set_xlabel("Number of samples")
        ax.set_ylabel("Crop label")
        ax.grid(axis="x", alpha=0.25)
        annotate_barh(ax, total=total)
        add_note_box(
            ax,
            "Scale: count (x-axis)\n"
            "Labels: count + % of Top10\n"
            "Colors: only distinguish crops",
        )
        save_fig(PLOTS_DIR / "01_crop_distribution_top10_labeled.png")

    # 2) Soil type distribution (if present)
    if "soil_type" in df.columns:
        vc = df["soil_type"].astype(str).value_counts()
        total = int(vc.sum())

        plt.figure(figsize=(10, 6))
        ax = sns.barplot(
            x=vc.index,
            y=vc.values,
            hue=vc.index,
            legend=False,
            palette="Set2",
        )
        ax.set_title("Soil type distribution (with percentage)")
        ax.set_xlabel("Soil type")
        ax.set_ylabel("Number of samples")
        ax.grid(axis="y", alpha=0.25)
        annotate_bar(ax, total=total)
        add_note_box(
            ax,
            "Scale: count (y-axis)\n"
            "Labels: count + % of total\n"
            "Colors: only distinguish soil types",
        )
        save_fig(PLOTS_DIR / "02_soil_type_distribution_labeled.png")

    # 3) Organic matter distribution (if present)
    if "organic_matter" in df.columns:
        series = df["organic_matter"].dropna()
        mean_val = float(series.mean()) if len(series) else 0.0

        plt.figure(figsize=(10, 6))
        ax = sns.histplot(series, bins=25, kde=True, color="#0d6efd")
        ax.axvline(mean_val, color="#dc3545", linestyle="--", linewidth=2, label=f"Mean = {mean_val:.2f}")
        ax.legend(loc="upper right")
        ax.set_title("Organic matter distribution (with mean)")
        ax.set_xlabel("Organic matter (%)")
        ax.set_ylabel("Frequency")
        add_note_box(
            ax,
            "Scale: % (x-axis)\n"
            "Bars: frequency (count)\n"
            "Red dashed: mean value",
        )
        save_fig(PLOTS_DIR / "03_organic_matter_distribution_mean.png")

    # 4) Correlation heatmap (numeric features)
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] >= 2:
        corr = numeric_df.corr(numeric_only=True).round(2)
        plt.figure(figsize=(11, 8))
        ax = sns.heatmap(
            corr,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            linewidths=0.5,
            cbar_kws={"label": "Correlation"},
        )
        ax.set_title("Correlation heatmap (numeric features)\n(Values near +1/-1 indicate strong relationship)")
        add_note_box(
            ax,
            "Scale: -1 to +1\n"
            "Red: positive\n"
            "Blue: negative\n"
            "White: ~0",
        )
        save_fig(PLOTS_DIR / "04_correlation_heatmap_annotated.png")

    # 5) pH vs rainfall scatter (sampled) with a trend line for readability
    if "ph" in df.columns and "rainfall" in df.columns:
        sample_n = min(SAMPLE_SIZE_SCATTER, len(df))
        sample = df.sample(sample_n, random_state=42) if sample_n > 0 else df

        plt.figure(figsize=(10, 6))
        ax = sns.regplot(
            data=sample,
            x="ph",
            y="rainfall",
            scatter_kws={"alpha": 0.35, "s": 25},
            line_kws={"color": "#dc3545", "linewidth": 2},
        )
        ax.set_title("pH vs Rainfall (sampled)\nRed line shows overall trend")
        ax.set_xlabel("Soil pH")
        ax.set_ylabel("Rainfall (mm)")
        ax.grid(alpha=0.25)
        add_note_box(
            ax,
            f"Scale: pH (x), mm (y)\n"
            f"Dots: samples (n={sample_n})\n"
            "Red line: trend",
        )
        save_fig(PLOTS_DIR / "05_ph_vs_rainfall_trend.png")

    print(f"Loaded dataset from: {source}")
    print(f"Saved plots to: {PLOTS_DIR}")


if __name__ == "__main__":
    main()

