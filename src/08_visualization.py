"""
08_visualization.py

This script generates basic visualizations for Fourier descriptors,
geometric descriptors, and classification results.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt


# ==========================================================
# USER CONFIGURATION
# ==========================================================

FOURIER_CSV = "results/fourier/fourier_summary.csv"
SHAPE_CSV = "results/tables/shape_descriptors.csv"
CLASSIFICATION_CSV = "results/tables/classification_tables.csv"

OUTPUT_DIR = "results/figures"


# ==========================================================
# PLOTTING FUNCTIONS
# ==========================================================

def save_histogram(data, xlabel, title, output_path, bins=25):
    """Save a histogram figure."""
    plt.figure(figsize=(8, 6))
    plt.hist(data.dropna(), bins=bins, edgecolor="black")
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    plt.title(title)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def save_pie_chart(table, method_name, output_path):
    """Save a pie chart for a selected classification method."""
    subset = table[table["Method"] == method_name].copy()

    if subset.empty:
        return

    subset = subset[subset["Absolute_frequency"] > 0]

    plt.figure(figsize=(7, 7))
    plt.pie(
        subset["Absolute_frequency"],
        labels=subset["Class"],
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops=dict(edgecolor="white")
    )
    plt.title(f"{method_name} classification")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df_fourier = pd.read_csv(FOURIER_CSV)
    df_shape = pd.read_csv(SHAPE_CSV)
    df_classification = pd.read_csv(CLASSIFICATION_CSV)

    save_histogram(
        df_fourier["Harmonics"],
        "Number of harmonics",
        "Distribution of Fourier harmonics",
        os.path.join(OUTPUT_DIR, "harmonics_histogram.png"),
        bins=30
    )

    save_histogram(
        df_shape["Circularity"],
        "Circularity",
        "Circularity distribution",
        os.path.join(OUTPUT_DIR, "circularity_histogram.png"),
        bins=25
    )

    save_histogram(
        df_shape["Roundness"],
        "Roundness",
        "Roundness distribution",
        os.path.join(OUTPUT_DIR, "roundness_histogram.png"),
        bins=25
    )

    save_histogram(
        df_shape["Regularity"],
        "Regularity",
        "Regularity distribution",
        os.path.join(OUTPUT_DIR, "regularity_histogram.png"),
        bins=25
    )

    for method in ["Wadell", "Powers", "Folk"]:
        save_pie_chart(
            df_classification,
            method,
            os.path.join(OUTPUT_DIR, f"{method.lower()}_pie_chart.png")
        )

    print(f"Figures saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()