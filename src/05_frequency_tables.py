"""
05_frequency_tables.py

This script builds frequency tables for Fourier harmonics and geometric
descriptors.
"""

import os
import pandas as pd


# ==========================================================
# USER CONFIGURATION
# ==========================================================

FOURIER_CSV = "results/fourier/fourier_summary.csv"
SHAPE_CSV = "results/tables/shape_descriptors.csv"

OUTPUT_DIR = "results/tables"
HARMONIC_LIMIT = 170


# ==========================================================
# FUNCTIONS
# ==========================================================

def build_frequency_table(series, bins, labels, variable_name):
    """Build absolute, relative, and cumulative frequency table."""
    categories = pd.cut(
        series,
        bins=bins,
        labels=labels,
        include_lowest=True,
        right=True
    )

    freq_abs = categories.value_counts().reindex(labels, fill_value=0)
    freq_rel = (freq_abs / len(series)) * 100
    freq_acum = freq_rel.cumsum()

    table = pd.DataFrame({
        "Variable": variable_name,
        "Class_interval": freq_abs.index,
        "Absolute_frequency": freq_abs.values,
        "Percentage": freq_rel.round(2).values,
        "Cumulative_percentage": freq_acum.round(2).values
    })

    return table


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df_fourier = pd.read_csv(FOURIER_CSV)
    df_shape = pd.read_csv(SHAPE_CSV)

    df_all = pd.merge(df_shape, df_fourier, on="Label", how="inner")

    # Keep only grains with harmonic number below the adopted threshold.
    df_base = df_all[df_all["Harmonics"] <= HARMONIC_LIMIT].copy()

    harmonic_bins = [0, 70, 100, 150, 170]
    harmonic_labels = ["0-70", "71-100", "101-150", "151-170"]

    descriptor_bins = [0.0, 0.5, 0.7, 0.85, 0.95, 1.0]
    descriptor_labels = ["Very low", "Low", "Moderate", "High", "Very high"]

    tables = []

    tables.append(
        build_frequency_table(
            df_base["Harmonics"],
            harmonic_bins,
            harmonic_labels,
            "Harmonics"
        )
    )

    for descriptor in ["Circularity", "Roundness", "Regularity"]:
        tables.append(
            build_frequency_table(
                df_base[descriptor],
                descriptor_bins,
                descriptor_labels,
                descriptor
            )
        )

    final_table = pd.concat(tables, ignore_index=True)

    output_path = os.path.join(OUTPUT_DIR, "frequency_tables.csv")
    final_table.to_csv(output_path, index=False)

    print(f"Frequency tables saved in: {output_path}")
    print(final_table)


if __name__ == "__main__":
    main()