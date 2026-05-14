"""
06_classification_models.py

This script classifies grains according to classical sedimentological
classification models: Wadell, Powers, and Folk.
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
# CLASSIFICATION FUNCTIONS
# ==========================================================

def classify_wadell(circularity):
    """Classify grain shape according to a Wadell-based circularity scale."""
    if circularity < 0.50:
        return "Very low"
    elif circularity < 0.70:
        return "Low"
    elif circularity < 0.85:
        return "Moderate"
    elif circularity < 0.95:
        return "High"
    else:
        return "Very high"


def classify_powers(roundness):
    """Classify grain roundness according to Powers."""
    if roundness < 0.15:
        return "Angular"
    elif roundness < 0.25:
        return "Subangular"
    elif roundness < 0.40:
        return "Subrounded"
    else:
        return "Rounded"


def classify_folk(roundness):
    """Classify textural maturity according to a Folk-based scale."""
    if roundness < 0.25:
        return "Immature"
    elif roundness < 0.50:
        return "Submature"
    elif roundness < 0.75:
        return "Mature"
    else:
        return "Supermature"


def build_classification_table(df, column_name, method_name):
    """Build a frequency table for a classification column."""
    freq_abs = df[column_name].value_counts()
    freq_rel = (freq_abs / len(df)) * 100

    table = pd.DataFrame({
        "Method": method_name,
        "Class": freq_abs.index,
        "Absolute_frequency": freq_abs.values,
        "Percentage": freq_rel.round(2).values
    })

    return table


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df_fourier = pd.read_csv(FOURIER_CSV)
    df_shape = pd.read_csv(SHAPE_CSV)

    df = pd.merge(df_shape, df_fourier, on="Label", how="inner")
    df = df[df["Harmonics"] <= HARMONIC_LIMIT].copy()

    df["Wadell_class"] = df["Circularity"].apply(classify_wadell)
    df["Powers_class"] = df["Roundness"].apply(classify_powers)
    df["Folk_class"] = df["Roundness"].apply(classify_folk)

    table_wadell = build_classification_table(df, "Wadell_class", "Wadell")
    table_powers = build_classification_table(df, "Powers_class", "Powers")
    table_folk = build_classification_table(df, "Folk_class", "Folk")

    final_table = pd.concat(
        [table_wadell, table_powers, table_folk],
        ignore_index=True
    )

    df.to_csv(os.path.join(OUTPUT_DIR, "grain_classifications.csv"), index=False)
    final_table.to_csv(os.path.join(OUTPUT_DIR, "classification_tables.csv"), index=False)

    print(f"Classified grains saved in: {OUTPUT_DIR}/grain_classifications.csv")
    print(f"Classification tables saved in: {OUTPUT_DIR}/classification_tables.csv")
    print(final_table)


if __name__ == "__main__":
    main()  