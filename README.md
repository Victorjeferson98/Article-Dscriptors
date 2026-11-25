# Article-Descriptors

**End-to-end segmentation and Fourier-based analysis of two-dimensional sedimentary-grain outlines in sandstone thin sections**

This repository supports the manuscript **“Automatic Fourier-based quantification of grain shape in sandstone thin sections: a reproducible workflow tested on the Faro Formation, Amazonas Basin.”** This README documents the **two supplied computational notebooks**, their execution order, formulas, processing parameters, generated products, and the differences that must be resolved before claiming exact numerical reproducibility of the revised manuscript.

> **Reproducibility status (important).** The documentation below was inspected against `segmentation(3).ipynb` and `fourier_modelo_final(20261123-203932).ipynb`. It does **not** imply that the notebooks were executed on the original petrographic images or that the manuscript tables were independently regenerated. In particular, the supplied Fourier notebook **does not yet implement every correction described in the revised article**. See [Critical discrepancies and required reconciliation](#critical-discrepancies-and-required-reconciliation).

## 1. Scientific scope and dataset

The workflow processes **2D profiles in petrographic photomicrographs**, not 3D grain shapes. The manuscript investigates four thin sections of the Mississippian Faro Formation, Amazonas Basin, Brazil:

| Sample | Well | Depth (m) |
|---|---|---:|
| Faro 12 | 1-GU-2-PA | 1738.00 |
| Faro 21 | 1-GU-2-PA | 1740.10 |
| Faro 32 | 2-LFST-1-AM | 2156.72 |
| Faro 41 | 2-LFST-1-AM | 2194.00 |

The manuscript reports a filtered population of **1,730 grains with retained harmonic order `H <= 170`**, including 1,038 from 1-GU-2-PA and 692 from 2-LFST-1-AM. This is **not** necessarily the full population processed by the Fourier routine.

## 2. Source notebooks and computational architecture

| Notebook | Cells | Purpose |
|---|---:|---|
| `segmentation(3).ipynb` | 2 | Photomicrograph preprocessing, marker-controlled watershed, candidate-grain labeling, individual-mask export, and historical RGB-rendered mask refinement |
| `fourier_modelo_final(20261123-203932).ipynb` | 18 | Binary-mask loading, contour sampling, FFT/IFFT reconstruction, fit diagnostics, geometric descriptors, spectral roughness, plots, frequency tables, historical classifications, Excel/CSV exports, and nine-sector analysis |

```text
Original RGB photomicrograph
  -> grayscale -> CLAHE -> Gaussian smoothing
  -> local threshold -> morphological cleanup
  -> Euclidean distance transform -> peak markers
  -> marker-controlled watershed -> labeled regions
  -> preview, masks, per-grain crops, CSV measurements
  -> rendered RGB watershed visualization (historical path)
  -> border removal -> per-color erosion -> binary mask
  -> connected-component labels -> centroid and contour
  -> angular ordering -> 360-point periodic radial interpolation
  -> FFT -> truncated IFFT -> R²/MSE/MAE and harmonic order H
  -> geometric descriptors and roughness coefficients
  -> distributions, comparative tables, nine-sector analysis
  -> figures, CSV and Excel outputs
```

**Do not confuse the RGB-color extraction in the second segmentation cell with RGB reference-color tolerance segmentation.** The former separates colors assigned to a **rendered watershed visualization**, not target mineral colors in the original photomicrograph.

## 3. Installation and environment

Python 3.10–3.11 is a reasonable environment for reproducing these notebooks, but **the exact package versions used for the published runs are not documented in the supplied files**. Record and pin tested versions before releasing an archival reproduction environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy scipy pandas matplotlib seaborn \
    scikit-image scikit-learn opencv-python pillow ipywidgets \
    notebook jupyterlab openpyxl
jupyter lab
```

The first segmentation notebook also imports `skimage.io`, `skimage.color`, `skimage.exposure`, `skimage.filters`, `skimage.feature`, `skimage.morphology`, `skimage.measure`, `skimage.segmentation`, and `scipy.ndimage`; these modules are included in the dependencies above. For provenance, save the actual environment after testing:

```bash
python -m pip freeze > requirements-lock.txt
```

## 4. Input preparation and paths

1. Obtain the original petrographic photomicrographs for each of the four thin sections, with sample identifiers and microscope acquisition metadata.
2. Keep each original image unchanged. Record its dimensions, file format, objective magnification, scale-bar information, and physical calibration when available.
3. Open `segmentation(3).ipynb`. Set `IMAGE_PATH` in cell 1 to the photomicrograph being processed and `OUTPUT_DIR` to a sample-specific output directory.
4. After the watershed processing, set `image_path` and `output_path` in cell 2. The historical second cell reads a **rendered RGB visualization** (`axes_individuais/08_graos_segmentados.png`) and writes a refined binary image.
5. Open `fourier_modelo_final(20261123-203932).ipynb`. Set `mask_path` in its main analysis cell to the binary image produced by segmentation cell 2. Update the absolute paths in later CSV/Excel export cells.

The uploaded notebooks contain **machine-specific `/home/victor/...` paths**; these are examples from the original development environment and will not work on another computer without editing. There is no verified command-line interface or automatic batch driver in the supplied notebooks. Run the two notebooks **for each sample**, preserving distinct output folders.

### Suggested project organization (recommended, not currently enforced by the code)

```text
Article-Descriptors/
├── README.md
├── segmentation(3).ipynb
├── fourier_modelo_final(20261123-203932).ipynb
├── data/
│   ├── Faro12/
│   ├── Faro21/
│   ├── Faro32/
│   └── Faro41/
└── results/
    ├── Faro12/
    ├── Faro21/
    ├── Faro32/
    └── Faro41/
```

Do not commit restricted or unlicensed photomicrographs without permission. The repository must explicitly identify which input images and historical masks correspond to the manuscript results.

## 5. Notebook 1: segmentation, step by step

### 5.1. Read RGB photomicrograph

`load_image(IMAGE_PATH)` uses `skimage.io.imread`. Grayscale inputs are expanded to three channels; additional channels such as alpha are discarded. The image is passed to the preprocessing routine as an RGB array.

### 5.2. Contrast enhancement and smoothing

`preprocess_image` performs:

1. RGB-to-grayscale conversion (`skimage.color.rgb2gray`);
2. contrast-limited adaptive histogram equalization, **CLAHE**, with `clip_limit=2.5`;
3. Gaussian smoothing with `sigma=1.0` pixel.

Smoothing is applied **before thresholding**, not as a separate post-Fourier operation.

### 5.3. Adaptive binary threshold

`build_binary_mask` converts the smoothed image to 8-bit intensity and calculates `skimage.filters.threshold_local` with `block_size=71` and `offset=-5` (8-bit intensity units). Foreground pixels satisfy `gray_u8 > local_thresh`. The sign of the offset and the comparison operator are part of the reproducible procedure.

### 5.4. Binary cleanup

`clean_mask` applies, in order:

- `remove_small_objects(..., min_size=120)`;
- `remove_small_holes(..., area_threshold=50)`;
- binary opening with `disk(1)`;
- binary closing with `disk(1)`.

All size thresholds in this notebook refer to **pixels**, not micrometers.

### 5.5. Euclidean distance transform and marker detection

`generate_markers` computes the Euclidean distance transform of the cleaned foreground. Each foreground pixel is assigned its distance to the nearest background pixel. The code locates internal maxima with `peak_local_max(min_distance=10, footprint=np.ones((15,15)))` and labels the marker image with `scipy.ndimage.label`.

The exact marker configuration should be checked in the code before editing library defaults. A marker is a candidate seed, **not independent proof that it identifies a distinct physical grain**.

### 5.6. Marker-controlled watershed

`apply_watershed` runs `watershed(-distance, markers, mask=cleaned_mask)`. Flooding the **negative** distance field from the detected markers partitions touching foreground regions into candidate grains. `filter_labeled_grains` retains labeled regions with area at least **150 pixels**; `FINAL_MAX_AREA=None` means no maximum-area filter is applied. Labels are reindexed consecutively.

A helper named `separate_touching_grains(labels, gap_size=1)` is **defined inside `main`**, as is a TIFF-export helper. In the uploaded code, these helpers are **not called** by `main`; do not describe the optional gap-removal helper as an automatically executed step.

### 5.7. Segmentation products

The first cell saves the following products under `OUTPUT_DIR`:

| Product | Content |
|---|---|
| `mascara_final.png` | Binary union of retained watershed regions |
| `overlay_contornos.png` | Candidate-region boundaries over the original image |
| `graos_numerados.png` | Numbered grain preview |
| `etapas_processamento.png` | Eight-panel processing overview |
| `axes_individuais/01_imagem_original.png` to `08_graos_segmentados.png` | Individual processing-stage figures |
| `graos_individuais/grao_XXXX.png` | Cropped original RGB grain regions |
| `mascaras_individuais/mask_grao_XXXX.png` | Cropped per-grain binary masks |
| `medidas_graos.csv` | Region measurements exported by `regionprops_table`, including computed circularity |

The numbered figures and individual masks are useful for visual quality control, but **visual inspection is not a quantitative segmentation-accuracy assessment**.

### 5.8. Historical mask refinement: second notebook cell

The second cell performs a separate, consequential processing step:

1. Load `axes_individuais/08_graos_segmentados.png`, a **rendered RGB image of watershed labels**.
2. Discard an alpha channel if present.
3. Treat exact `[0, 0, 0]` pixels as background and all nonblack pixels as candidate foreground.
4. Apply `clear_border` to remove foreground components touching the image border.
5. Enumerate distinct nonblack RGB values in the rendered image.
6. For each exact RGB color, construct a color-specific mask, intersect it with the border-cleared foreground, and erode it using `disk(1)`.
7. Combine the eroded color masks and save a binary PNG (`08_graos_binaria_sem_borda_com_lacuna01.png` in the current hard-coded path).

**Methodological warning:** because the input is a **rendered visualization**, antialiasing, color quantization, interpolation, and image-background colors can alter the extracted regions. The code does not use the original integer watershed labels for this final mask. A future direct-label implementation is preferable, but must first be benchmarked against the archived masks; replacing it silently would change the experiment.

### 5.9. Segmentation parameter reference

| Parameter | Current value | Role |
|---|---:|---|
| `CLAHE_CLIP_LIMIT` | 2.5 | Contrast enhancement |
| `GAUSSIAN_SIGMA` | 1.0 px | Gaussian smoothing |
| `LOCAL_BLOCK_SIZE` | 71 px | Adaptive-threshold neighborhood |
| `LOCAL_OFFSET` | -5 | Adaptive-threshold offset on 8-bit image |
| `MIN_OBJECT_AREA` | 120 px | Remove small binary objects |
| `MIN_HOLE_AREA` | 50 px | Fill small holes |
| `MORPH_DISK_SIZE` | 1 px | Opening/closing |
| `MIN_DISTANCE_PEAKS` | 10 px | Peak separation |
| `FOOTPRINT_SIZE` | 15 px | Local-maxima neighborhood |
| `FINAL_MIN_AREA` | 150 px | Minimum watershed region |
| `FINAL_MAX_AREA` | `None` | No maximum watershed area |
| `erosion_radius` (cell 2) | 1 px | Erode rendered-color regions |

## 6. Notebook 2: Fourier and morphometric analysis, step by step

### 6.1. Load the binary mask and label grains

The first analysis cell loads `mask_path` using Pillow, converts it to a NumPy array, and creates a binary mask with `np.array(mask_img) > 0`. `analyze_grains(binary_mask)` calls `scipy.ndimage.label`, iterates over connected components, and excludes regions with **fewer than 20 pixels**. Each retained grain is assigned an integer label, and its centroid is calculated using `scipy.ndimage.center_of_mass`.

**Notebook execution note:** the main cell already invokes `analyze_grains` under `if __name__ == '__main__'`, and the following cell invokes it **again** as `results, labels_array = analyze_grains(mask_array)`. In a normal Jupyter kernel, `__name__` is usually `__main__`, so executing the cells in order can analyze the same mask twice. This is a runtime inefficiency; it does not establish two independent experimental replicates.

### 6.2. Contour extraction and 360-point radial sampling

`calculate_radii(region, center, num_angles=360)`:

1. extracts candidate contours with `skimage.measure.find_contours(region.astype(float), 0.5)`;
2. selects the **longest** contour;
3. computes polar coordinates relative to the centroid, `r_j = sqrt((x_j-x_c)^2+(y_j-y_c)^2)` and `theta_j = atan2(y_j-y_c, x_j-x_c) mod 2π`;
4. sorts vertices by angle and removes duplicate angular values, keeping the first encountered radius;
5. interpolates the radial distances periodically with `np.interp(..., period=2*pi)` onto `theta_k = 2πk/360`, for `k = 0,...,359`.

This is **angular interpolation of contour vertices**, **not first-exit ray casting**. Non-star-shaped grains can have several boundary intersections at one angle; the one-valued radial representation may therefore lose contour details.

The function **multiplies interpolated radii by `px_to_um`**. The actual uploaded code sets `px_to_um = 0.072`. This setting **must be reconciled** with the revised manuscript's unverified-calibration statement before assigning physical units to the outputs.

### 6.3. Fourier coefficients and reconstruction

The sampled radial profile is transformed using `scipy.fft.fft`:

```text
C_m = sum_{k=0}^{N-1} r_k exp(-2π i m k / N)
```

The function `fourier_series(radii, num_harmonics)` zeroes coefficients with indices from `H+1` through `N-H-1`, retaining the zero-frequency term, the first `H` positive frequencies, and their conjugate negative frequencies. The real part of the inverse FFT (`ifft`) gives the reconstructed radial profile. The equivalent real-series form is

```text
r_H(theta) = r_0 + sum_{n=1}^{H} [A_n cos(n theta) + B_n sin(n theta)]
```

Low-order terms represent broad shape variation; higher orders capture finer variations **at the image's spatial resolution**, including possible segmentation noise.

`calculate_fourier_descriptors(radii, n_descriptors=64)` additionally returns the first 64 values of `abs(fft(radii))/N`. These are **not normalized by the mean radius** in the supplied function and therefore should not be described as fully scale-invariant.

### 6.4. Harmonic-order selection: actual stopping rule

The uploaded code sets:

```python
min_harmonics = 1
max_harmonics = 300
target_r2 = 0.999
epsilon = 1e-5
upper_limit = min(max_harmonics, len(radii) // 2)
for H in range(min_harmonics, upper_limit):
    # reconstruct, compute MSE and R², and test stopping criteria
    ...
```

For 360 angular samples, `upper_limit=180` and the exclusive `range` examines **H=1,...,179**. At each step the code calculates `mean_squared_error` and `r2_score`. It stops when either:

- `R² >= 0.999`; or
- the **absolute relative change** in MSE compared with the preceding candidate is below `1e-5`.

If the MSE-improvement condition fires, the stored `best_*` values may still correspond to the **previous** harmonic order because the code breaks before updating them. Consequently, this procedure is **early stopping**, **not** global minimization of MSE and not an independently validated optimal harmonic count. The code also records MAE and a per-grain history of `H`, MSE, and R² values evaluated before stopping.

The `results` dictionary includes `labels`, `areas`, `centers`, `MAE`, `MSE`, `R2`, `harmonics`, `radii_real`, `radii_fourier`, `angles`, and `history`.

### 6.5. Reconstruction metrics

For original radial samples `r_k` and reconstructed samples `r_hat_k`:

```text
MAE = (1/N) sum_k |r_k - r_hat_k|
MSE = (1/N) sum_k (r_k - r_hat_k)^2
R²  = 1 - sum_k (r_k - r_hat_k)^2 / sum_k (r_k - mean(r))^2
```

MSE has the **square of the units assigned to `r_k`**. Because the notebook multiplies radii by `0.072`, its MSE is scaled by `0.072²` relative to raw-pixel MSE. Without verified calibration, labeling this result as µm² is not justified. **R² does not validate segmentation accuracy:** it only compares the extracted radial signal with its truncated Fourier representation.

### 6.6. Geometric descriptors and the two implementations of regularity

The notebook contains **two separate implementations**:

**Primary analysis cell (`calculate_geometric_descriptors`)**:

```text
CI = 4πA / P²
RO = 2 sqrt(πA) / P = sqrt(CI)
RE_legacy = log(P / (P - P_conv)), if P > P_conv; otherwise 0
```

**Later descriptor cell (`calculate_shape_descriptors`)**:

```text
CI = 4πA / P²
RO = 2 sqrt(πA) / P = sqrt(CI)
CP = P_conv / P
```

Here `A` is segmented pixel area, `P` is the measured perimeter, and `P_conv` is the convex-hull perimeter. The later `CP` formula is the one used in the **revised manuscript**. The primary cell's logarithmic `RE_legacy` is **not equivalent** to `CP`; do not merge their outputs or label them interchangeably. The notebook still contains a sector-analysis comment referring to the logarithmic definition. A cleaned release should use one explicit `CP` implementation throughout.

The variable `RO` in these routines is an **area–perimeter index**, algebraically redundant with circularity; it is **not** Wadell's corner-roundness measurement. The independent set in an algebraic sense is therefore CI, CP and H, but their **statistical independence has not been demonstrated**.

### 6.7. Fourier roughness coefficients

`calculate_roughness_coefficients(coeffs, j, k)` calculates:

```text
P_(j,k) = sqrt(0.5 * sum_{n=j}^{k} [Re(C_n)^2 + Im(C_n)^2])
```

The notebook also generates low-, medium-, and high-frequency roughness summaries and includes them in later per-grain and sector analyses. Their numeric values depend on the FFT coefficient normalization and the selected frequency intervals. Inspect the relevant cells before comparing these values with another roughness convention; do not assume that this quantity is automatically a physical RMS roughness in micrometers.

### 6.8. Visual diagnostics

The notebook provides plots for:

- MSE and R² evolution against retained harmonic order for selected grains;
- comparisons between extracted and reconstructed outlines;
- polar and Cartesian `r(theta)` representations;
- grouped histograms for circularity, roundness, regularity and H;
- pie charts and frequency summaries;
- nine-sector spatial maps and sector-wise descriptor summaries.

These figures are **diagnostics and descriptive comparisons**. They do not replace a manually traced reference dataset for testing segmentation accuracy.

### 6.9. The `H <= 170` analysis subset

A later cell builds `df_fourier` from grain labels and harmonic orders, joins it to `df_shape`, and defines:

```python
df_all = pd.merge(df_shape, df_fourier, on="Label", how="inner")
df_base = df_all[df_all["Harmônicos"] <= 170].copy()
N = len(df_base)
```

All frequencies calculated from `df_base` are **conditional on this filter**. The filter does not change the Fourier fitting itself; it selects a subset for subsequent frequency tables and historical classifications. The notebook uses different bin sets in different cells, so **record the bin edges and boundary inclusion rule for every exported table**. `pd.cut(..., include_lowest=True, right=True)` includes the upper edge in each bin; this is not identical to every half-open interval convention in the manuscript.

### 6.10. Historical Wadell/Powers/Folk labeling: exploratory only

The supplied notebook still includes `classify_wadell`, `classify_powers`, and `classify_folk`, and exports their labels and pie charts. These routines map **CI or RO to arbitrary numerical thresholds**. Because RO is not Wadell corner roundness and Folk's textural maturity is not a per-grain function of this RO index, these outputs **must not be presented as validated Wadell, Powers or Folk classifications**. The revised manuscript instead reports explicitly defined **numerical circularity intervals**. Keep historical classification cells only as archived exploratory analyses or remove them from a cleaned reproduction branch; they are not part of the manuscript's accepted interpretive workflow.

The manuscript's Table 6 uses these circularity intervals:

| Circularity interval | 1-GU-2-PA (n) | 2-LFST-1-AM (n) |
|---|---:|---:|
| CI < 0.50 | 169 | 55 |
| 0.50 <= CI < 0.70 | 505 | 339 |
| 0.70 <= CI < 0.85 | 317 | 268 |
| 0.85 <= CI < 0.95 | 45 | 28 |
| CI >= 0.95 | 2 | 2 |
| **Total** | **1,038** | **692** |

These are **reported manuscript counts**, not counts recalculated in preparing this README.

### 6.11. Nine-sector (3 × 3) analysis

The last notebook cell divides the mask image into a 3 × 3 grid and assigns each grain to a sector based on its centroid. The spatial layout is NW/N/NE, W/C/E, and SW/S/SE (with the center sector labeled C). It constructs per-grain and per-sector data frames for grain counts, Fourier reconstruction metrics, H, geometric descriptors, roughness and area, and produces maps, summary tables, CSV and Excel files.

The code uses image coordinates, where row increases downward; sector labels are **image-relative**, not geographic compass bearings unless image orientation has been established. Some variable labels in this cell still refer to `mse_um2` and to the logarithmic regularity formula. These labels require correction if the output is to be interpreted under the revised manuscript's calibration and descriptor conventions.

### 6.12. Tables and exports

The notebook creates several frequency tables and exports Excel and CSV outputs, including:

- grain-level geometric descriptors;
- filtered (`H <= 170`) Fourier/geometry tables;
- exploratory historical classifications;
- combined comparison tables;
- nine-sector grain-level and aggregated statistics.

Export paths are hard-coded to the original machine in multiple cells. The current workbook names are not a stable, parameterized output API; adapt paths per sample and retain a record of the code version, input mask, calibration setting, and bin definitions used for each table. The notebook uses `openpyxl` as the Excel writer engine.

## 7. End-to-end execution checklist

1. **Archive inputs:** store the original image, sample ID, image dimensions, acquisition settings and any physical scale information.
2. **Configure segmentation:** edit `IMAGE_PATH` and `OUTPUT_DIR` in the first cell of `segmentation(3).ipynb`.
3. **Run segmentation cell 1:** inspect `etapas_processamento.png`, `overlay_contornos.png`, `mascara_final.png`, numbered grains, individual masks and `medidas_graos.csv`.
4. **Configure mask refinement:** point segmentation cell 2 to the actual `08_graos_segmentados.png`; set its binary-mask output path; run and inspect the result.
5. **Configure Fourier analysis:** set `mask_path` to that refined binary mask; explicitly decide whether `px_to_um` represents a **verified** physical calibration. For an uncalibrated analysis, use pixel units consistently and document any numerical change from the archived runs.
6. **Run Fourier cells in order:** avoid unnecessary duplicate execution of `analyze_grains`; verify that the `results` dictionary and `df_shape` refer to the **same input mask**.
7. **Review geometric descriptors:** use the later `CP = P_conv/P` definition for manuscript-aligned regularity; do not report the legacy logarithmic `RE` as CP.
8. **Create plots and frequency tables:** distinguish the full reconstruction population from the filtered `H <= 170` subset; check bin edges and denominators.
9. **Do not interpret exploratory historical labels** as independent Wadell, Powers or Folk classifications.
10. **Run sector analysis** only after all prerequisite variables exist and agree in length; inspect labels and units.
11. **Export outputs:** save per-sample tables, plots, masks, parameter values and software versions; maintain a mapping between generated files and manuscript figures/tables.
12. **Verify reproduction:** compare counts, descriptive statistics, sample identities and figures against the archived study outputs. Report mismatches rather than adjusting results without explanation.

## 8. Critical discrepancies and required reconciliation

The following items were **observed directly in the supplied notebooks** and should be resolved **in code and/or in the manuscript** before describing the repository as a fully reproducible release:

| Issue | Supplied notebook | Revised manuscript / required interpretation |
|---|---|---|
| Physical scale | Fourier cell sets `px_to_um = 0.072` and scales radii and areas | Manuscript states calibration is unverified and treats radial errors as pixel-based. Confirm provenance and units; do not silently replace historical values. |
| Regularity | Primary Fourier cell uses `log(P/(P-P_conv))`; later geometric cell uses `P_conv/P` | Manuscript defines perimeter-based `CP = P_conv/P`. Consolidate calculations and downstream labels. |
| Historical labels | Notebook contains Wadell/Powers/Folk threshold functions and charts | Manuscript rejects these as independent grain-level classification schemes; keep as legacy only. |
| MSE column naming | Sector cell uses `mse_um2` and “MSE (µm²)” | Physical units require verified calibration; update column names or document calibration. |
| Segmentation provenance | Second segmentation cell processes rendered RGB watershed visualization | This is the documented historical method; replacing it with direct integer-label masks requires a controlled equivalence test. |
| Duplicate execution | Fourier main cell and next cell both call `analyze_grains` | Run once per input mask in a cleaned workflow. |
| Harmonic order | Early stopping at `R² >= 0.999` or relative MSE change below `1e-5` | Do not describe `H` as a global MSE minimizer or independent complexity estimate. |
| Frequency bins | Multiple notebook cells use different edges and `pd.cut(..., right=True)` | Reconcile manuscript table intervals, edge inclusion, and filtered population before regenerating tables. |
| Absolute paths | Inputs and exports point to `/home/victor/...` | Parameterize per sample and remove machine-specific assumptions. |
| Input availability | Notebook paths reference local images/masks | Publish permitted source images or an accessible, immutable input manifest with checksums. |

**These are not merely README wording issues.** Some change computed quantities or their scientific interpretation. Updating documentation alone does not fix a mismatch between archived code and manuscript methods.

## 9. Validation, interpretation and limitations

- **Fourier reconstruction fidelity:** MAE, MSE and R² measure the agreement between an **extracted radial profile** and its truncated harmonic representation. High R² is partly driven by the harmonic stopping criterion.
- **Segmentation accuracy:** no grain-matched expert masks were supplied to this review. Quantitative overlap or boundary accuracy (e.g., Dice, IoU, boundary displacement) **has not been demonstrated** by these notebooks.
- **Petrographic comparison:** conventional petrographic observations provide qualitative sedimentological context, not per-grain ground-truth segmentation masks.
- **Two-dimensional stereology:** thin-section cuts, mineralogy, grain size, orientation, cement and overgrowths can all affect measured contours.
- **Spectral resolution:** high harmonic order may encode real geometric detail or segmentation/sampling artifacts; its geological meaning requires sensitivity analysis.
- **Sampling scope:** four thin sections from two wells are insufficient to infer basin-wide depositional energy, transport distance or provenance from outline indices alone.
- **Timing:** manuscript estimates of ~7 minutes per section computationally versus ~180 minutes conventional petrography are not an equivalent-task benchmark.

## 10. Manuscript reference statistics (not regenerated here)

The revised manuscript reports mean Fourier reconstruction **R² = 0.9989**, mean **MSE = 0.0008**, and mean retained harmonic order **H = 118.3**. These are reference values from the manuscript; their numerical reproducibility depends on the exact historical masks, code version, calibration setting, and selected population. The reported MSE units should not be inferred from the value alone.

## 11. Recommended reproducibility improvements

1. Preserve a frozen **historical** notebook and masks associated with published tables.
2. Create a separate, clearly versioned **manuscript-aligned** notebook after resolving calibration and regularity discrepancies.
3. Export watershed **integer labels** directly in a new branch and compare them quantitatively with historical RGB-derived masks before adopting them.
4. Consolidate repeated descriptor functions and ensure every plot, CSV and sector table uses the same verified formulas and units.
5. Add a machine-readable input manifest, per-sample configuration file, fixed dependencies, test data and checksums.
6. Add a grain-matched manual-contour validation subset and uncertainty analysis when these data become available.

## 12. Attribution and citation

**Developer:** Victor J. C. Moreira. **Language:** Python 3. **Study:** Faro Formation, Amazonas Basin, Brazil. Cite the associated manuscript and the archived release/DOI when available. No software license is inferred from the supplied notebooks; check the repository's `LICENSE` before reuse or redistribution.

---

**Documentation basis:** `segmentation(3).ipynb`, `fourier_modelo_final(20261123-203932).ipynb`, and the revised manuscript discussed with the authors. This README intentionally distinguishes **implemented behavior**, **historical exploratory outputs**, and **manuscript-aligned interpretation**.
