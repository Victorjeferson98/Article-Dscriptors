# Source Code

This folder contains the Python scripts used in the grain morphology analysis workflow.

The code is organized according to the main processing steps of the project:

## 01_segmentation.py

Performs image segmentation and grain separation.

Main tasks:

- image loading;
- grayscale conversion;
- contrast enhancement;
- smoothing;
- binary mask generation;
- morphological cleaning;
- distance transform;
- marker-controlled watershed;
- grain labeling.

## 02_fourier_descriptors.py

Extracts grain contours and represents them using Fourier descriptors.

Main tasks:

- contour extraction;
- center of mass calculation;
- polar radius sampling;
- Fourier reconstruction;
- harmonic optimization;
- MSE, MAE and R² calculation.

## 03_shape_descriptors.py

Calculates geometric descriptors for each grain.

Main descriptors:

- area;
- perimeter;
- circularity;
- roundness;
- regularity.

## 04_classification_tables.py

Builds textural classification tables based on classical sedimentological models.

Included classifications:

- Wadell;
- Powers;
- Folk.

## 05_export_results.py

Exports the results to spreadsheet files.

Main outputs:

- individual grain descriptors;
- Fourier descriptors;
- frequency tables;
- textural classification tables.

## 06_visualization.py

Generates the graphical outputs used for interpretation.

Main figures:

- segmented grains;
- Fourier reconstruction;
- MSE and R² curves;
- harmonic histograms;
- descriptor histograms;
- pie charts.
