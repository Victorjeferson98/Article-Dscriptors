"""
03_fourier_analysis.py

This script extracts grain contours from a binary mask and reconstructs each
grain boundary using Fourier descriptors.
"""

import os
import warnings
import numpy as np
import pandas as pd

from scipy.fft import fft, ifft
from scipy.ndimage import center_of_mass, label
from skimage.io import imread
from skimage.measure import find_contours
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

warnings.filterwarnings("ignore")


# ==========================================================
# USER CONFIGURATION
# ==========================================================

MASK_PATH = "results/segmentation/binary_mask_no_border_with_gaps.png"
OUTPUT_DIR = "results/fourier"

PX_TO_UM = 0.072
MIN_HARMONICS = 1
MAX_HARMONICS = 300
NUM_ANGLES = 360
MIN_GRAIN_PIXELS = 20


# ==========================================================
# FOURIER FUNCTIONS
# ==========================================================

def load_binary_mask(mask_path):
    """Load a binary mask from disk."""
    mask = imread(mask_path)

    if mask.ndim == 3:
        mask = mask[..., 0]

    return mask > 0


def calculate_radii(region, center, num_angles=360):
    """Extract r(theta) from the real grain contour using fixed angular sampling."""
    contours = find_contours(region.astype(float), 0.5)

    if len(contours) == 0:
        raise ValueError("No contour found for this grain.")

    contour = max(contours, key=len)

    cy, cx = center

    y = contour[:, 0]
    x = contour[:, 1]

    x_rel = x - cx
    y_rel = y - cy

    angles = np.arctan2(y_rel, x_rel)
    angles = np.mod(angles, 2 * np.pi)

    radii = np.sqrt(x_rel**2 + y_rel**2)

    order = np.argsort(angles)
    angles = angles[order]
    radii = radii[order]

    unique_angles, unique_indices = np.unique(angles, return_index=True)

    angles = unique_angles
    radii = radii[unique_indices]

    theta_uniform = np.linspace(0, 2 * np.pi, num_angles, endpoint=False)

    radii_uniform = np.interp(
        theta_uniform,
        angles,
        radii,
        period=2 * np.pi
    )

    return theta_uniform, radii_uniform


def fourier_reconstruction(radii, num_harmonics):
    """Reconstruct the radial signal using a limited number of Fourier harmonics."""
    coeffs = fft(radii)

    filtered_coeffs = np.zeros_like(coeffs, dtype=complex)

    filtered_coeffs[0] = coeffs[0]

    filtered_coeffs[1:num_harmonics + 1] = coeffs[1:num_harmonics + 1]
    filtered_coeffs[-num_harmonics:] = coeffs[-num_harmonics:]

    reconstructed = np.real(ifft(filtered_coeffs))

    return reconstructed


def find_optimal_harmonics(radii, min_harmonics=1, max_harmonics=300):
    """Find the harmonic number that minimizes reconstruction error."""
    harmonics_list = []
    mse_list = []
    mae_list = []
    r2_list = []

    best_h = None
    best_mse = np.inf
    best_reconstruction = None

    for h in range(min_harmonics, max_harmonics + 1):
        reconstructed = fourier_reconstruction(radii, h)

        mse = mean_squared_error(radii, reconstructed)
        mae = mean_absolute_error(radii, reconstructed)
        r2 = r2_score(radii, reconstructed)

        harmonics_list.append(h)
        mse_list.append(mse)
        mae_list.append(mae)
        r2_list.append(r2)

        if mse < best_mse:
            best_mse = mse
            best_h = h
            best_reconstruction = reconstructed

    history = {
        "harmonics": harmonics_list,
        "MSE": mse_list,
        "MAE": mae_list,
        "R2": r2_list
    }

    return best_h, best_reconstruction, history


def analyze_grains(binary_mask):
    """Analyze all grains in a binary mask using Fourier descriptors."""
    labels_array, num_labels = label(binary_mask)

    results = {
        "labels": [],
        "centers": [],
        "angles": [],
        "radii_real": [],
        "radii_fourier": [],
        "harmonics": [],
        "mse": [],
        "mae": [],
        "r2": [],
        "history": []
    }

    for label_id in range(1, num_labels + 1):
        region = labels_array == label_id

        if np.sum(region) < MIN_GRAIN_PIXELS:
            continue

        center = center_of_mass(region)

        try:
            angles, radii_px = calculate_radii(region, center, NUM_ANGLES)
        except ValueError:
            continue

        radii_um = radii_px * PX_TO_UM

        best_h, best_reconstruction, history = find_optimal_harmonics(
            radii_um,
            MIN_HARMONICS,
            MAX_HARMONICS
        )

        mse = mean_squared_error(radii_um, best_reconstruction)
        mae = mean_absolute_error(radii_um, best_reconstruction)
        r2 = r2_score(radii_um, best_reconstruction)

        results["labels"].append(label_id)
        results["centers"].append(center)
        results["angles"].append(angles)
        results["radii_real"].append(radii_um)
        results["radii_fourier"].append(best_reconstruction)
        results["harmonics"].append(best_h)
        results["mse"].append(mse)
        results["mae"].append(mae)
        results["r2"].append(r2)
        results["history"].append(history)

    return results, labels_array


def save_fourier_outputs(results, labels_array, output_dir):
    """Save Fourier analysis results."""
    os.makedirs(output_dir, exist_ok=True)

    df = pd.DataFrame({
        "Label": results["labels"],
        "Harmonics": results["harmonics"],
        "MSE": results["mse"],
        "MAE": results["mae"],
        "R2": results["r2"]
    })

    df.to_csv(os.path.join(output_dir, "fourier_summary.csv"), index=False)

    np.savez_compressed(
        os.path.join(output_dir, "fourier_data.npz"),
        labels=np.array(results["labels"], dtype=object),
        centers=np.array(results["centers"], dtype=object),
        angles=np.array(results["angles"], dtype=object),
        radii_real=np.array(results["radii_real"], dtype=object),
        radii_fourier=np.array(results["radii_fourier"], dtype=object),
        labels_array=labels_array
    )

    return df


def main():
    binary_mask = load_binary_mask(MASK_PATH)

    results, labels_array = analyze_grains(binary_mask)
    df = save_fourier_outputs(results, labels_array, OUTPUT_DIR)

    print(f"Fourier analysis completed.")
    print(f"Processed grains: {len(results['labels'])}")
    print(f"Results saved in: {OUTPUT_DIR}")
    print(df.head())


if __name__ == "__main__":
    main()