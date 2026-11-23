# Article-Descriptors

**Reproducible two-dimensional grain-outline characterization in sandstone thin sections using image segmentation, geometric descriptors, and radial Fourier reconstruction**

This repository accompanies the manuscript **“Automatic Fourier-based quantification of grain shape in sandstone thin sections: a reproducible workflow tested on the Faro Formation, Amazonas Basin.”** It documents the processing decisions used to extract candidate grain regions from petrographic photomicrographs, represent their boundaries as radial signals, reconstruct those signals with truncated Fourier series, and summarize their geometric characteristics.

> **Scope and provenance.** This README describes the **revised manuscript methodology**. It is not a claim that every script in a local checkout has been independently executed or verified. Before publishing a reproducibility release, confirm that the archived notebooks, input masks, script order, dependencies, and output tables correspond exactly to the manuscript. In particular, do **not** replace the historical RGB-rendered watershed-mask stage with direct integer-label export without checking equivalence.

## 1. Study dataset

Four petrographic thin sections of the Mississippian Faro Formation (Amazonas Basin, Brazil) were examined, with two sections from each well.

| Sample | Well | State | Depth (m) |
|---|---|---|---:|
| Faro 12 | 1-GU-2-PA | Pará | 1738.00 |
| Faro 21 | 1-GU-2-PA | Pará | 1740.10 |
| Faro 32 | 2-LFST-1-AM | Amazonas | 2156.72 |
| Faro 41 | 2-LFST-1-AM | Amazonas | 2194.00 |

The study characterizes **two-dimensional grain profiles**, not the original three-dimensional grain shapes. A subset of **1,730 profiles** meeting the exploratory filter `H <= 170` is reported in the manuscript's circularity-frequency table (1,038 from 1-GU-2-PA; 692 from 2-LFST-1-AM). This filtered count must not be presented as the number of all segmented grains or all Fourier reconstructions.

## 2. Processing overview

```text
Petrographic RGB photomicrographs
    |
    v
Grayscale conversion -> CLAHE -> Gaussian smoothing
    |
    v
Local adaptive threshold -> binary cleanup
    |
    v
Euclidean distance transform -> local-maximum markers
    |
    v
Marker-controlled watershed -> candidate grain regions
    |
    v
Historical RGB-rendered region-mask preparation
    |  (remove border regions; identify nonblack colors; erode)
    v
Archived binary grain masks
    |
    v
Longest contour -> centroid -> polar coordinates
    |
    v
Angular sorting + periodic interpolation (360 samples)
    |
    v
FFT -> truncated inverse FFT with early stopping
    |
    +--> R², MSE, retained harmonic order H
    |
    v
Circularity (CI), area-perimeter index (RO),
perimeter-based regularity (CP)
    |
    v
Grain-level summaries, histograms, section/well comparisons,
and qualitative comparison with conventional petrography
```

## 3. Requirements and environment

- Python 3
- NumPy, SciPy, pandas
- OpenCV (`opencv-python`), scikit-image, scikit-learn
- Matplotlib, seaborn, Pillow
- Jupyter, if running the notebook-based workflow

Example installation in an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Linux / macOS
python -m pip install --upgrade pip
python -m pip install numpy scipy pandas opencv-python scikit-image scikit-learn matplotlib seaborn pillow jupyter
```

This is an **illustrative installation command**, not a locked or tested dependency specification. For an archival release, add the tested package versions and Python version to `requirements.txt` or an environment lockfile.

## 4. Step-by-step methodology

### Step 1 — Load and preprocess the images

Read each RGB petrographic image and apply the following operations in sequence:

1. Convert RGB to grayscale.
2. Apply contrast-limited adaptive histogram equalization (**CLAHE**, clip limit **2.5**).
3. Apply Gaussian smoothing with **sigma = 1.0 pixel**.
4. Apply locally adaptive thresholding to the smoothed 8-bit image, with **block size = 71 pixels** and **offset = -5 intensity units**.

Record image dimensions, original filenames, image type, and preprocessing settings for each sample. The manuscript does not establish a verified physical image scale; do not interpret an image scale bar or a notebook multiplier as calibrated micrometres per pixel without a separate calibration check.

### Step 2 — Clean the binary candidate-grain mask

After thresholding:

- Remove binary objects smaller than **120 pixels**.
- Fill holes smaller than **50 pixels**.
- Apply morphological opening and closing with a **disk of radius 1 pixel**.

These operations produce the foreground mask used for marker detection. The area thresholds refer to **pixel counts**, not square micrometres.

### Step 3 — Separate touching candidate grains using watershed

Compute the Euclidean distance transform of the cleaned binary mask:

$$
D(x,y)=\min_{(u,v)\in\Omega_b}\sqrt{(x-u)^2+(y-v)^2},
$$

where $\Omega_b$ denotes the background pixels.

Detect local maxima with the parameters documented in the manuscript:

| Parameter | Value |
|---|---:|
| Minimum peak distance | 10 pixels |
| Peak-detection footprint | 15 × 15 pixels (square) |
| Watershed elevation | Negative distance transform, `-D` |
| Watershed domain | Cleaned binary foreground mask |
| Minimum retained watershed-region area | 150 pixels |
| Maximum region area | No limit specified |

Label the detected markers and run marker-controlled watershed. This stage is intended to separate candidate grain regions that touch within the binary foreground. It is **not** quantitatively validated against expert-traced boundaries in the reported study.

### Step 4 — Prepare the historical masks used for the published results

**This is a provenance-critical stage.** The workflow documented in the revised manuscript did not directly feed integer watershed labels into the Fourier analysis. Instead, the historical implementation:

1. Saved or loaded a **rendered RGB visualization** of the watershed regions.
2. Treated pixels **different from black** as foreground.
3. Removed foreground components touching the image border using `clear_border`.
4. Treated each distinct nonblack RGB value as an individual color mask.
5. Eroded each color mask using a **disk of radius 1 pixel**.
6. Combined the eroded masks into the binary image subsequently analyzed.

The RGB-rendered intermediate may be affected by antialiasing, background colors, and color quantization. Preserve the original rendered files and final archived masks when reproducing the published values. A future direct export from watershed integer labels may be preferable, but it must be benchmarked against the historical masks before being described as equivalent.

**Do not insert RGB reference-color tolerance segmentation or DBSCAN into the published workflow.** These appear in earlier methodological drafts, but the revised manuscript explicitly states that they were not part of the inspected segmentation notebook.

### Step 5 — Extract contours and construct the radial signal

For each retained binary region:

1. Compute its geometric centroid from the foreground pixels.
2. Extract contours at the **0.5 isolevel** and select the **longest contour**.
3. For each contour vertex $(x_j,y_j)$, compute polar coordinates relative to centroid $(x_c,y_c)$:

$$
\theta_j=\operatorname{atan2}(y_j-y_c,x_j-x_c),\qquad
r_j=\sqrt{(x_j-x_c)^2+(y_j-y_c)^2}.
$$

4. Sort contour vertices by their polar angle.
5. Periodically interpolate the radial distances onto **N = 360** equally spaced angular positions:

$$
\theta_k=\frac{2\pi k}{360},\qquad k=0,\ldots,359.
$$

This is **angular interpolation of extracted contour vertices**, **not first-exit ray casting**. Non-star-shaped or strongly concave boundaries may have several contour points at similar angles; representing them with a single-valued radial function can lose geometric information.

### Step 6 — Reconstruct each radial contour with Fourier harmonics

Apply the discrete Fourier transform to the 360-point radial profile:

$$
R_m=\sum_{k=0}^{N-1}r_k\exp\!\left(-\frac{2\pi i m k}{N}\right).
$$

For harmonic order $H$, retain the zero-frequency coefficient, the positive-frequency coefficients up to $H$, and their conjugate negative-frequency counterparts. Set other coefficients to zero and apply the inverse transform. The equivalent real-valued representation is

$$
r_H(\theta)=r_0+\sum_{n=1}^{H}\left[A_n\cos(n\theta)+B_n\sin(n\theta)\right].
$$

The inspected implementation evaluates **H = 1, ..., 179** and uses **early stopping** at the first of:

- $R^2\geq0.999$; **or**
- relative MSE improvement below $10^{-5}$.

The selected $H$ is **not** the global minimizer of MSE over the full search interval. Because the second condition can trigger first, some retained reconstructions can have $R^2<0.999$. The subset `H <= 170` is an **analysis filter** used for some frequency summaries, not the reconstruction search limit.

### Step 7 — Compute reconstruction diagnostics

For each original radial profile $r_k$ and reconstruction $\widetilde r_k$:

$$
\mathrm{MSE}=\frac{1}{N}\sum_{k=1}^{N}(r_k-\widetilde r_k)^2,
$$

$$
R^2=1-\frac{\sum_{k=1}^{N}(r_k-\widetilde r_k)^2}{\sum_{k=1}^{N}(r_k-\bar r)^2}.
$$

Record at least the grain identifier, sample identifier, retained order $H$, MSE, and $R^2$. Handle the zero-variance case explicitly: $R^2$ is undefined for a perfectly constant radial profile.

**Interpretation:** MSE and $R^2$ measure the fidelity of Fourier reconstruction to the **extracted contour**, not the correctness of segmentation relative to the physical grain boundary. In the uncalibrated workflow, radial distances remain in pixels and MSE has units **pixel²**.

### Step 8 — Compute geometric descriptors

Using segmented area $A$, contour perimeter $P$, and convex-hull perimeter $P_{\mathrm{conv}}$:

| Descriptor | Definition | Interpretation |
|---|---|---|
| Circularity (`CI`) | $CI=4\pi A/P^2$ | Global two-dimensional area–perimeter compactness |
| Area–perimeter index (`RO`) | $RO=2\sqrt{\pi A}/P=\sqrt{CI}$ | Deterministic transformation of circularity; **not** Wadell corner roundness |
| Perimeter-based regularity (`CP`) | $CP=P_{\mathrm{conv}}/P$ | Ratio of convex-hull perimeter to measured perimeter |

**Important:** `RO` and `CI` are algebraically redundant and must not be presented as independent evidence. The reported `CP` definition replaces the older logarithmic regularity formula. Solidity ($A/A_{\mathrm{conv}}$), three-dimensional sphericity, and Wadell corner roundness are **different** measurements and must not be substituted for these descriptors. Pixel-grid perimeter conventions can affect numerical results; document the exact function and parameters used.

### Step 9 — Aggregate results and compare with petrography

Generate grain-level tables, per-section histograms, class-frequency summaries, and selected contour-versus-reconstruction plots. Compare the computed distributions with the **independent conventional petrographic descriptions** of the same thin sections.

The manuscript's exploratory circularity intervals for profiles meeting `H <= 170` are:

- `CI < 0.50`
- `0.50 <= CI < 0.70`
- `0.70 <= CI < 0.85`
- `0.85 <= CI < 0.95`
- `CI >= 0.95`

These are **numerical bins**, not Wadell roundness categories, Powers visual-chart classes, or Folk maturity classes. The sector-level conventional observations are qualitative and are not matched-grain numerical reference masks.

## 5. Repository organization and execution order

The manuscript's Code availability statement identifies processing components numbered **01–08** and an additional sector-analysis notebook. The exact filenames and command-line interfaces were **not provided with this README request**, so the list below is a logical execution guide, **not a verified filesystem listing**:

| Logical stage | Manuscript component | Required input | Expected output |
|---|---|---|---|
| 01 | Segmentation | Original photomicrographs | Watershed regions / rendered RGB visualization |
| 02 | Mask preparation | Rendered watershed visualization | Archived grain masks |
| 03 | Fourier analysis | Grain masks | Radial profiles, harmonic orders, reconstruction diagnostics |
| 04 | Shape descriptors | Grain masks and contours | `CI`, `RO`, `CP` per grain |
| 05 | Frequency tables | Per-grain measurements | Section/well summaries and filtered counts |
| 06 | Classifications | Descriptor tables | Numerical-bin summaries (check actual code before using) |
| 07 | Export | Computed measurements | Tabular results |
| 08 | Visualization | Masks, contours, measurements | Figures and comparison plots |
| Separate notebook | Sector-level analysis | Petrographic sector observations and computed indices | Qualitative sector comparisons |

### Reproduction checklist

1. Obtain the four original images, historical watershed RGB visualizations, and **archived masks** associated with the manuscript.
2. Record the exact Python environment, library versions, and source-code revision.
3. Execute the repository's actual scripts/notebooks **in their documented order**, verifying file paths and expected inputs. Do not assume the stage labels above are executable filenames.
4. Preserve grain identifiers and the mapping between each original image, archived mask, and measurement table.
5. Recalculate per-grain Fourier diagnostics using **360 samples** and the documented early-stopping rule.
6. Verify that `CI`, `RO`, and `CP` follow the formulas above, with `RO² = CI` within numerical precision.
7. Apply `H <= 170` **only** where the manuscript uses that exploratory filter; keep unfiltered reconstruction statistics separate.
8. Compare the regenerated tables and figures with the archived manuscript outputs; document any differences rather than silently overwriting historical results.

## 6. Reference values reported in the manuscript

These are **reported study results**, not automatically verified test fixtures for the present repository checkout.

| Reconstruction statistic | Reported value |
|---|---:|
| Mean $R^2$ | 0.9989 |
| Median $R^2$ | 0.9990 |
| Minimum $R^2$ | 0.7062 |
| Mean MSE | 0.0008 |
| Median MSE | 0.0005 |
| Mean retained $H$ | 118.3 |
| Median retained $H$ | 132 |
| Observed $H$ range | 4–179 |

**Circularity-bin subset (`H <= 170`):**

| CI interval | 1-GU-2-PA | 2-LFST-1-AM |
|---|---:|---:|
| `< 0.50` | 169 | 55 |
| `[0.50, 0.70)` | 505 | 339 |
| `[0.70, 0.85)` | 317 | 268 |
| `[0.85, 0.95)` | 45 | 28 |
| `>= 0.95` | 2 | 2 |
| **Total** | **1,038** | **692** |

The manuscript also reports approximate processing times of **7 minutes per section** for the computational workflow and **180 minutes per section** for conventional petrographic examination, on the study workstation. These procedures perform **different analytical tasks**, and the comparison is not a standardized benchmark or proof of equivalent accuracy.

## 7. Limitations and validation status

- **Segmentation accuracy is not quantitatively validated.** No expert-traced, grain-matched reference masks were available to estimate overlap, false splits/merges, or boundary displacement.
- **Fourier reconstruction accuracy is not segmentation accuracy.** High $R^2$ is partly influenced by the harmonic selection criterion.
- **Spatial calibration is unverified.** The notebook settings `px_to_um=1.0` and `CALIBRATION_VERIFIED=False` do **not** establish a physical scale. Report radial quantities in pixels and radial MSE in pixel² unless independently calibrated.
- **The historical RGB-rendered watershed step is fragile.** Antialiasing and color quantization can change region identities; retain its archived intermediate outputs for reproducibility.
- **Single-valued radial interpolation has geometric limits**, particularly for non-star-shaped outlines.
- **Two-dimensional thin-section profiles are not unbiased 3D particle-shape measurements.** Grain orientation, sectioning, cement, overgrowths, and image resolution can affect the observations.
- **The sample is limited to four thin sections.** Between-well and geological interpretations are descriptive, not basin-scale causal inference.
- **Independent statistical validation and uncertainty estimates are limited.** Do not infer significance from small differences in percentages alone.

### Recommended future validation

Compare automatic masks with expert-traced reference masks sampled across all four sections. Report grain matching, intersection-over-union or Dice overlap, boundary-distance metrics, split/merge rates, and uncertainty by sample. Also test sensitivity to image resolution, segmentation thresholds, contour interpolation, and harmonic stopping rules. These are **future validation recommendations**, not experiments already completed in the manuscript.

## 8. Reproducibility release checklist

Before describing this repository as fully reproducible, provide or verify:

- [ ] Original images and their permitted redistribution status
- [ ] Historical RGB watershed renderings and archived binary masks
- [ ] Actual script/notebook filenames, their execution order, and input/output paths
- [ ] Tested dependency versions and environment specification
- [ ] Explicit random seeds where applicable
- [ ] Per-grain raw results and unfiltered/filtered sample counts
- [ ] Image calibration evidence, or an explicit statement that calibration is unavailable
- [ ] Consistent perimeter computation and descriptor definitions
- [ ] Automated consistency checks comparing regenerated and archived tables
- [ ] A stable repository release identifier (tag/commit/DOI)

## 9. Citation and authorship

If using this workflow, cite the accompanying manuscript once its final bibliographic information is available:

> Moreira, V. J. C., Machado, Y. C. P., Gonçalves, J. F. V., Santos, T. S., Delaunay, N., Soares, J. L., and de Figueiredo, J. J. S. *Automatic Fourier-based quantification of grain shape in sandstone thin sections: a reproducible workflow tested on the Faro Formation, Amazonas Basin.* Manuscript; publication details pending.

**Developer:** Victor J. C. Moreira  
**Repository named in the manuscript:** https://github.com/Victorjeferson98/Article-Dscriptors  
**Language:** Python 3

## 10. License and data access

A software license and data redistribution permissions were **not established by the provided manuscript or methodology text**. Add a `LICENSE` file and a data-access statement after confirming the rights associated with the source photomicrographs, masks, and petrographic descriptions. Do not assume that publicly accessible code or images are automatically licensed for unrestricted reuse.

---

**Documentation basis:** revised manuscript methodology and appendices (23 November 2026). This README intentionally supersedes earlier descriptions involving DBSCAN, RGB reference-color tolerance, first-exit ray casting, logarithmic regularity, and global-MSE minimization because those descriptions do not match the revised manuscript's documented processing sequence.
