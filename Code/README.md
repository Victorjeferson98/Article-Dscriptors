# Petrographic Grain Segmentation and Fourier-Based Morphological Analysis

This repository contains two Jupyter notebooks for processing petrographic thin-section images, separating sedimentary grains, reconstructing their two-dimensional contours using Fourier analysis, and computing geometric and spectral descriptors.

> **Execution status:** This README documents the supplied notebooks as inspected. They contain machine-specific file paths and an execution issue described under **Known issues**. The notebooks were not modified or end-to-end validated as part of this documentation.

## 1. Repository contents

| Notebook | Purpose |
| --- | --- |
| `segmentation.ipynb` | Image preprocessing, binary segmentation, marker-controlled watershed, grain separation, visualizations and measurements. |
| `fourier_modelo_final.ipynb` | Polar contour extraction, Fourier reconstruction, reconstruction-error assessment, geometric descriptors, classifications, frequency tables and spatial sector analysis. |

## 2. Processing workflow

```text
Petrographic RGB image
        |
        v
segmentation_EN.ipynb
  Grayscale -> CLAHE -> Gaussian smoothing
  -> local threshold -> morphological cleaning
  -> distance transform -> peak markers -> watershed
  -> grain filtering -> masks, images and measurements
        |
        v
Binary grain mask (preferably with separated grains)
        |
        v
fourier_modelo_final_EN.ipynb
  Connected components -> grain contours -> polar r(theta)
  -> Fourier reconstruction -> MAE / MSE / R²
  -> geometric and spectral descriptors
  -> frequency tables / classifications / 3x3 sectors
        |
        v
Figures, CSV and Excel tables
```

## 3. Requirements and installation

Python 3.10 or 3.11 and JupyterLab or Jupyter Notebook are reasonable starting points. The notebooks import the following packages (no locked versions are supplied):

```bash
python3 -m venv .venv
source .venv/bin/activate             # Linux/macOS
python -m pip install --upgrade pip
python -m pip install jupyterlab numpy pandas matplotlib scipy scikit-image opencv-python scikit-learn seaborn ipywidgets pillow openpyxl
jupyter lab
```

On Windows, activate the environment with `.venv\Scripts\activate`. Alternatively, open the notebooks in VS Code with a Python/Jupyter kernel or upload them to Google Colab and install any missing dependencies.

## 4. Notebook 1 — `segmentation_EN.ipynb`

### 4.1 Input and configuration

Open the notebook and edit the configuration at the beginning of **cell 1**:

```python
IMAGE_PATH = "/path/to/your/thin_section.jpg"
OUTPUT_DIR = "saida_segmentacao_graos01"

CLAHE_CLIP_LIMIT = 2.5
GAUSSIAN_SIGMA = 1.0
LOCAL_BLOCK_SIZE = 71
LOCAL_OFFSET = -5
MIN_OBJECT_AREA = 120
MIN_HOLE_AREA = 50
MORPH_DISK_SIZE = 1
MIN_DISTANCE_PEAKS = 10
FOOTPRINT_SIZE = 15
FINAL_MIN_AREA = 150
FINAL_MAX_AREA = None
```

`IMAGE_PATH` must point to an existing petrographic image. `OUTPUT_DIR` is created by the notebook. The parameters above are the values found in the supplied notebook, not universally optimized settings.

| Parameter | Function |
| --- | --- |
| `CLAHE_CLIP_LIMIT` | Local contrast enhancement strength. |
| `GAUSSIAN_SIGMA` | Gaussian smoothing intensity. |
| `LOCAL_BLOCK_SIZE`, `LOCAL_OFFSET` | Local binary-threshold settings. |
| `MIN_OBJECT_AREA`, `MIN_HOLE_AREA` | Remove small objects and fill small holes. |
| `MORPH_DISK_SIZE` | Morphological structuring-element size. |
| `MIN_DISTANCE_PEAKS`, `FOOTPRINT_SIZE` | Detection of grain-center markers for watershed. |
| `FINAL_MIN_AREA`, `FINAL_MAX_AREA` | Final connected-grain area filtering in pixels. |

### 4.2 Run the segmentation

1. Open `segmentation.ipynb`.
2. Change `IMAGE_PATH` and, if needed, `OUTPUT_DIR`.
3. Execute the first code cell. It defines the processing functions and invokes `main()`.
4. Inspect the segmentation preview and output files before proceeding.
5. Execute the second code cell **only after configuring its own input and output paths** (see below).

The first cell performs grayscale conversion, CLAHE enhancement, Gaussian smoothing, local thresholding, morphological cleaning, distance-transform marker generation, marker-controlled watershed, grain filtering, visualizations, and exports.

### 4.3 Segmentation outputs

The first cell writes results to `OUTPUT_DIR`, including:

- `overlay_contornos.png` — extracted grain boundaries overlaid on the image.
- `mascara_final.png` — binary foreground mask (255 for grains, 0 for background).
- `graos_numerados.png` — preview with grain labels.
- `etapas_processamento.png` — overview of processing stages.
- `medidas_graos.csv` — region-property measurements.
- `axes_individuais/` — stage-by-stage processing images, including `08_graos_segmentados.png`.
- Individual grain images and masks saved by `save_individual_grains()`.

The code also defines a helper named `save_separated_grains_tif()`; **it is not called in the inspected first cell**, so do not assume that `graos_separados.tif` will be generated automatically.

### 4.4 Second cell: border removal and grain separation

The second cell is a distinct postprocessing step. It reads a color-coded segmentation image, treats black pixels as background, removes components touching the image border using `clear_border`, processes individual colors, applies erosion and exports a binary image with gaps between grains.

Edit its two hard-coded paths:

```python
image_path = "/path/to/saida_segmentacao_graos01/axes_individuais/08_graos_segmentados.png"
output_path = "/path/to/output/08_graos_binaria_sem_borda_com_lacuna01.png"
```

Make sure the destination directory exists before running the cell. The output is the intended binary-mask input for the Fourier notebook. Verify that individual grains are distinct and that valid grains have not been lost through erosion or border removal.

## 5. Notebook 2 — `fourier_modelo_final_EN.ipynb`

### 5.1 Input and calibration

The notebook expects a binary grain mask, with foreground pixels representing grains. Its second cell contains:

```python
px_to_um = 0.072
min_harmonics = 1
max_harmonics = 300
```

**Important:** `px_to_um = 0.072` is the calibration value currently written in the notebook; verify the true micrometers-per-pixel scale for each image before interpreting physical dimensions.

In the same cell, replace the hard-coded `mask_path` with the binary image produced by the segmentation notebook:

```python
mask_path = "/path/to/output/08_graos_binaria_sem_borda_com_lacuna01.png"
```

### 5.2 Fourier reconstruction

The main analysis:

1. Identifies labeled grain components from the binary mask.
2. Extracts grain outlines and represents them as a radial function `r(theta)` with 360 angular samples (1° increments).
3. Computes Fourier-based contour representations and tests harmonic counts.
4. Evaluates reconstructed contours using mean absolute error (MAE), mean squared error (MSE), and coefficient of determination (R²).
5. Stores per-grain reconstruction histories and measurements in `results`.

The code uses a reconstruction-quality target and stopping criterion inside `analyze_grains()`. Inspect the function before changing these conditions; the maximum harmonic setting alone does not guarantee that every grain will use that many harmonics.

### 5.3 Notebook cell sequence

| Cell (1-based) | Content |
| --- | --- |
| 1 | Imports. |
| 2 | Calibration, Fourier functions, grain analysis and image loading. |
| 3 | Invocation of `analyze_grains()` and assignment of `results, labels_array`. |
| 4–5 | Reconstruction metrics versus harmonics for selected grains. |
| 6 | Extracted versus reconstructed contours. |
| 7 | Interactive polar grain visualization (`ipywidgets`). |
| 8 | Harmonic-count histogram. |
| 9 | Radial-function plots. |
| 10 | Shape descriptors and `df_shape`. |
| 11 | Descriptor histograms. |
| 12 | Fixed-population frequency tables (`df_base`, using harmonics ≤ 170). |
| 13 | Pie charts from frequency tables. |
| 14 | Wadell, Powers and Folk classifications. |
| 15 | Excel export of descriptors and classifications. |
| 16 | Combined comparison/frequency table and CSV export. |
| 17 | Two separate summary tables. |
| 18 | Spatial 3 × 3 sector analysis and sector exports. |

Execute the cells in order **after resolving the execution issue below**. Later cells depend on variables and tables defined in earlier cells; running them out of order can cause `NameError` or stale results.

### 5.4 Interpreting outputs

- **MAE, MSE and R²:** assess agreement between the original and reconstructed radial contours. Their interpretation depends on the radii's units and normalization.
- **Harmonic count:** number of terms selected for the reconstruction under the notebook's stopping rule.
- **Circularity, roundness and regularity:** shape descriptors calculated by the notebook. Check the exact implementations before comparing values with external classification systems.
- **Spectral roughness:** coefficients computed from harmonic bands.
- **Wadell, Powers and Folk:** code-defined classification rules, which should not be presented as externally validated ground truth without methodological justification.
- **3 × 3 sectors:** spatial grouping of grain measurements across nine image sectors (NW, N, NE, W, C, E, SW, S, SE).

The notebook writes an Excel workbook for descriptor/classification results, a combined comparison CSV, and sector-analysis Excel/CSV files. Some output destinations are currently absolute paths; change them to writable locations on your system.

## 6. Known issues and checks before running

### 6.1 Inconsistent return-value assignment in the Fourier notebook

At the end of Fourier **cell 2**, the inspected code includes:

```python
results = analyze_grains(mask_array)
```

However, `analyze_grains()` returns **two values** (`results, labels_array`). As written, `results` becomes a tuple at that point. **Cell 3** subsequently contains the correct unpacking:

```python
results, labels_array = analyze_grains(mask_array)
```

For a clean execution, update the assignment at the end of cell 2 to `results, labels_array = analyze_grains(mask_array)` and avoid redundantly rerunning the full analysis in cell 3, or otherwise restructure these two cells consistently. This README does **not** apply that fix to the notebook itself.

### 6.2 Absolute file paths

Both notebooks contain paths beginning with `/home/victor/...`. These are local to the original workstation. Update the segmentation input, the second segmentation cell's paths, the Fourier mask input, and the Fourier CSV/Excel output paths.

### 6.4 Data and validation

- No sample thin-section image is bundled with these two notebooks.
- No automated segmentation validation or manual reference contours are supplied here.
- Segmentation quality should be inspected visually and, for quantitative claims, assessed against independent reference masks.
- Confirm pixel calibration, grain-size filters, reconstruction settings and classification thresholds for every sample.
- Do not treat the output statistics as results from a reproducible run until the notebooks have been executed successfully on the intended dataset.

## 7. Suggested GitHub structure

```text
repository/
├── README.md
├── segmentation.ipynb
├── fourier_modelo_final.ipynb
├── data/
│   └── README.md                 # Explain how to obtain input images
└── results/                      # Optional generated outputs
```

Avoid committing private data, very large raw image collections or machine-specific output folders without checking repository size and data-sharing permissions. Consider a separate data archive with a DOI for publication-quality reproducibility.

## 8. Reproducibility checklist

- [ ] Set valid image paths and output directories.
- [ ] Install the Python dependencies.
- [ ] Run the first segmentation cell and inspect its outputs.
- [ ] Configure and run the second segmentation cell to create the separated binary mask.
- [ ] Confirm the mask contains the intended grain population.
- [ ] Set the Fourier notebook's `mask_path` and physical pixel calibration.
- [ ] Resolve the duplicate/inconsistent `analyze_grains()` invocation.
- [ ] Run the Fourier cells in order.
- [ ] Inspect reconstruction plots, descriptors, classifications and sector tables.
- [ ] Export and archive the final figures, CSV and Excel results.
- [ ] Record the dataset identifier, image resolution, calibration, package versions and parameters for each experiment.

## 9. Scientific use

The workflow supports two-dimensional grain-shape characterization from petrographic imagery. Interpretations of sedimentary transport, depositional processes or textural maturity require geological context and independent evidence; grain-shape descriptors alone are not a unique indicator of depositional environment.

If this repository accompanies a manuscript, add the article citation, authors, DOI (when available), data availability statement and an explicit software license before release.
