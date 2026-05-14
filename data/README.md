# Data Directory

This directory contains all datasets used during the workflow of the project.

The data are organized according to the processing stage.

---

# Directory Structure

```text
data/
│
├── raw/
├── processed/
├── masks/
├── contours/
└── README.md
```

---

# raw/

Contains the original petrographic images used as input for segmentation and Fourier analysis.

Examples:

```text
data/raw/faro_12.png
data/raw/lamina_32.png
```

These images are typically RGB microscopy images acquired from thin sections.

---

# processed/

Contains intermediate preprocessing outputs.

Typical preprocessing operations include:

- grayscale conversion;
- contrast enhancement;
- CLAHE;
- Gaussian smoothing;
- normalization.

Example files:

```text
data/processed/grayscale/
data/processed/enhanced/
data/processed/smoothed/
```

---

# masks/

Contains binary masks and segmented grain images.

## binary_masks/

Binary masks generated after thresholding.

Example:

```text
binary_mask.png
```

---

## watershed/

Watershed segmentation outputs.

Example:

```text
watershed_labels.png
```

---

## labeled/

Labeled grain images.

Each grain receives a unique label or color.

Example:

```text
labeled_grains.png
```

---

# contours/

Contains contour data extracted from segmented grains.

---

## cartesian/

Stores grain contours in Cartesian coordinates.

Example:

```text
grain_001_xy.csv
```

Columns:

- x
- y

---

## polar/

Stores grain contours in polar coordinates.

Example:

```text
grain_001_rt.csv
```

Columns:

- theta
- radius

These files are used for Fourier descriptor analysis.

---

# Notes

The workflow begins with images stored in `raw/`.

All subsequent directories contain intermediate or processed outputs generated during the analysis pipeline.
