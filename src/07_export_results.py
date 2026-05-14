"""
07_export_results.py

This script exports the final project results to an Excel workbook.
"""

import os
import pandas as pd


# ==========================================================
# USER CONFIGURATION
# ==========================================================

GRAIN_CLASSIFICATIONS_CSV = "results/tables/grain_classifications.csv"
FREQUENCY_TABLES_CSV = "results/tables/frequency_tables.csv"
CLASSIFICATION_TABLES_CSV = "results/tables/classification_tables.csv"
FOURIER_CSV = "results/fourier/fourier_summary.csv"
SHAPE_CSV = "results/tables/shape_descriptors.csv"

OUTPUT_EXCEL = "results/tables/final_results.xlsx"


# ==========================================================
# MAIN FUNCTION
# ==========================================================

def main():
    os.makedirs(os.path.dirname(OUTPUT_EXCEL), exist_ok=True)

    df_models = pd.read_csv(GRAIN_CLASSIFICATIONS_CSV)
    df_frequency = pd.read_csv(FREQUENCY_TABLES_CSV)
    df_classification = pd.read_csv(CLASSIFICATION_TABLES_CSV)
    df_fourier = pd.read_csv(FOURIER_CSV)
    df_shape = pd.read_csv(SHAPE_CSV)

    with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as writer:
        df_models.to_excel(writer, sheet_name="Grain_models", index=False)
        df_frequency.to_excel(writer, sheet_name="Frequency_tables", index=False)
        df_classification.to_excel(writer, sheet_name="Classification_tables", index=False)
        df_fourier.to_excel(writer, sheet_name="Fourier_summary", index=False)
        df_shape.to_excel(writer, sheet_name="Shape_descriptors", index=False)

    print(f"Final Excel workbook saved in: {OUTPUT_EXCEL}")


if __name__ == "__main__":
    main()