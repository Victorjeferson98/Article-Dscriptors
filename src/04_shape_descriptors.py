"""
04_shape_descriptors.py

This script calculates geometric shape descriptors for each segmented grain.
"""

import os
import numpy as np
import pandas as pd

from scipy.ndimage import label
from skimage.io import imread
from skimage.measure import regionprops
from skimage.morphology import convex_hull_image


# ==========================================================
# USER CONFIGURATION
# ==========================================================

MASK_PATH = "results/segmentation/binary_mask_no_border_with_gaps.png"
OUTPUT_PATH = "results/tables/shape_descriptors.csv"

PX_TO_UM = 0.072
MIN_GRAIN_PIXELS = 20


# ==========================================================
# FUNCTIONS
# ==========================================================

def load_binary_mask(mask_path):
    """Load binary mask from disk."""
    mask = imread(mask_path)

    if mask.ndim == 3:
        mask = mask[..., 0]

    return mask > 0


def calculate_shape_descriptors(binary_mask, px_to_um=1.0):
    """Calculate geometric descriptors for each grain."""
    labels_array, num_labels = label(binary_mask)

    descriptors = {
        "Label": [],
        "Area_um2": [],
        "Perimeter_um": [],
        "Circularity": [],
        "Roundness": [],
        "Regularity": []
    }

    for label_idx in range(1, num_labels + 1):
        region = labels_array == label_idx

        if np.sum(region) < MIN_GRAIN_PIXELS:
            continue

        props = regionprops(region.astype(int))[0]

        area = props.area * (px_to_um ** 2)
        perimeter = props.perimeter * px_to_um

        if perimeter == 0:
            continue

        # Circularity measures similarity to a perfect circle.
        circularity = (4 * np.pi * area) / (perimeter ** 2)

        # Convex hull is used to estimate shape regularity.
        convex_hull = convex_hull_image(region)
        convex_area = np.sum(convex_hull) * (px_to_um ** 2)

        if convex_area == 0:
            continue

        # Roundness approximation based on the relation between area and convex area.
        roundness = area / convex_area

        # Regularity combines circularity and roundness.
        regularity = np.sqrt(circularity * roundness)

        descriptors["Label"].append(label_idx)
        descriptors["Area_um2"].append(area)
        descriptors["Perimeter_um"].append(perimeter)
        descriptors["Circularity"].append(circularity)
        descriptors["Roundness"].append(roundness)
        descriptors["Regularity"].append(regularity)

    return pd.DataFrame(descriptors)


def main():
    binary_mask = load_binary_mask(MASK_PATH)
    df_shape = calculate_shape_descriptors(binary_mask, PX_TO_UM)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df_shape.to_csv(OUTPUT_PATH, index=False)

    print(f"Shape descriptors saved in: {OUTPUT_PATH}")
    print(df_shape.head())


if __name__ == "__main__":
    main()