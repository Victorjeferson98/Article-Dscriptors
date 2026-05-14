# Source Code

This directory contains all Python scripts used in the workflow for petrographic grain segmentation, Fourier descriptor extraction, morphological characterization, statistical analysis, and visualization of results.

The scripts were organized according to the logical sequence of the methodology proposed in the article.

---

# Repository Workflow

The complete workflow of the project is illustrated below:

```text
Petrographic Image
        ↓
Image Preprocessing
        ↓
Segmentation and Grain Separation
        ↓
Contour Extraction
        ↓
Fourier Descriptor Analysis
        ↓
Geometric Descriptor Calculation
        ↓
Textural Classification
        ↓
Statistical Analysis
        ↓
Visualization and Export of Results
```

---

# Installation

Before running the scripts, install all project dependencies.

## 1. Clone the repository

```bash
git clone https://github.com/Victorjeferson98/Article-Dscriptors.git
```

## 2. Enter the repository folder

```bash
cd Article-Dscriptors
```

## 3. Install the required libraries

```bash
pip install -r requirements.txt
```

---



# 01_segmentation.py

# Objective

This script performs the preprocessing and segmentation of petrographic images in order to isolate individual grains from the background.

The segmentation stage is one of the most important steps of the workflow because all subsequent analyses depend on the quality of the extracted grain boundaries.

---

# Main Operations

The script performs the following operations:

## 1. Image loading

The petrographic image is loaded from the input directory.

Example:

```python
image_path = "data/raw/sample_image.png"
```

---

## 2. Color conversion

The image may be converted to grayscale or RGB depending on the segmentation strategy.

---

## 3. Contrast enhancement

Contrast enhancement techniques may be applied to improve grain visibility.

Typical operations:

- CLAHE
- Histogram equalization
- Intensity normalization

---

## 4. Noise reduction

Noise reduction filters are applied to smooth the image before segmentation.

Examples:

- Gaussian filter
- Median filter

---

## 5. Binary mask generation

The grains are separated from the background using thresholding techniques.

Methods may include:

- Otsu thresholding
- Color masking
- Manual thresholding

---

## 6. Morphological cleaning

Morphological operations remove artifacts and improve grain connectivity.

Typical operations:

- Binary opening
- Binary closing
- Hole filling
- Small object removal

---

## 7. Watershed grain separation

Connected grains are separated using marker-controlled watershed segmentation.

Operations:

- Euclidean Distance Transform
- Local maxima detection
- Watershed segmentation

---

## 8. Grain labeling

Each segmented grain receives a unique label for later processing.

---

# Input

Example input image:

```text
data/raw/sample_image.png
```

---

# Output

Generated outputs may include:

```text
data/processed/segmented_image.png

results/figures/segmentation_result.png

results/figures/labeled_grains.png
```

---

# How to Run

Edit the image path inside the script:

```python
image_path = "data/raw/sample_image.png"
```

Run:

```bash
python src/01_segmentation.py
```

---

# 02_fourier_descriptors.py

# Objective

This script extracts grain contours and models their morphology using Fourier descriptors.

The Fourier representation converts the grain boundary into harmonic components that quantify shape complexity and roughness.

---

# Main Operations

## 1. Load segmented image

The segmented or labeled image generated in the previous step is loaded.

---

## 2. Contour extraction

The external contour of each grain is extracted.

Typical methods:

- skimage.measure.find_contours
- OpenCV contours

---

## 3. Center of mass calculation

The centroid of each grain is computed.

---

## 4. Polar coordinate transformation

The contour is converted from Cartesian coordinates to polar coordinates.

---

## 5. Radial sampling

The radial distance is sampled as a function of angle:

```text
r(θ)
```

---

## 6. Fourier decomposition

The radial signal is decomposed into harmonic components using Fourier series.

---

## 7. Fourier reconstruction

The contour is reconstructed using different harmonic orders.

---

## 8. Reconstruction metrics

The reconstruction quality is evaluated using:

- MSE
- MAE
- R²

---

# Input

```text
data/processed/segmented_image.png
```

---

# Output

```text
results/contours/

results/tables/fourier_descriptors.csv

results/figures/fourier_reconstruction.png

results/figures/mse_curve.png

results/figures/r2_curve.png
```

---

# How to Run

Edit the input image path:

```python
segmented_image_path = "data/processed/segmented_image.png"
```

Run:

```bash
python src/02_fourier_descriptors.py
```

---

# 03_shape_descriptors.py

# Objective

This script computes geometric descriptors for each grain.

These descriptors quantify grain morphology and are later used for sedimentological interpretation.

---

# Main Descriptors

## Area

Projected grain area.

---

## Perimeter

Length of the grain boundary.

---

## Circularity

Measures similarity to a perfect circle.

---

## Roundness

Measures edge smoothness.

---

## Regularity

Measures contour regularity and symmetry.

---

# Input

```text
results/tables/fourier_descriptors.csv
```

---

# Output

```text
results/tables/shape_descriptors.csv
```

---

# How to Run

```bash
python src/03_shape_descriptors.py
```

---

# 04_classification_tables.py

# Objective

This script classifies the grains according to classical sedimentological classification schemes.

---

# Included Classifications

## Wadell (1932)

Classification based on grain sphericity and circularity.

---

## Powers (1953)

Classification based on grain roundness.

Classes:

- Angular
- Subangular
- Subrounded
- Rounded

---

## Folk (1951)

Classification based on textural maturity.

Classes:

- Immature
- Submature
- Mature
- Supermature

---

# Input

```text
results/tables/shape_descriptors.csv
```

---

# Output

```text
results/tables/classification_tables.csv
```

---

# How to Run

```bash
python src/04_classification_tables.py
```

---

# 05_export_results.py

# Objective

This script exports the final results into spreadsheet files for interpretation and publication.

---

# Exported Data

The exported tables may include:

- Fourier descriptors
- Geometric descriptors
- Harmonic statistics
- Classification frequencies
- Textural maturity tables

---

# Output

```text
results/tables/final_results.xlsx
```

---

# How to Run

```bash
python src/05_export_results.py
```

---

# 06_visualization.py

# Objective

This script generates the graphical outputs used in the article.

---

# Generated Figures

## Segmentation Figures

- Binary masks
- Watershed segmentation
- Labeled grains

---

## Fourier Reconstruction Figures

- Real contour
- Fourier reconstructed contour
- Polar representation

---

## Statistical Figures

- MSE curves
- R² curves
- Harmonic histograms
- Circularity histograms
- Roundness histograms
- Regularity histograms

---

## Classification Figures

- Pie charts
- Frequency distributions
- Comparative plots between wells

---

# Output

```text
results/figures/
```

---

# How to Run

```bash
python src/06_visualization.py
```

---

# Notes

## Important

The scripts should always be executed sequentially because the outputs generated by one stage are used as inputs in subsequent stages.

---

# Notebook Version

Interactive notebook implementations are available in the `notebooks/` directory.

These notebooks contain:

- step-by-step execution;
- intermediate visualizations;
- parameter tuning;
- experimental tests.

---

# Suggested Citation

If you use this repository in academic work, please cite the associated article.
