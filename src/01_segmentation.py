"""
01_segmentation.py

This script performs image preprocessing, binary segmentation, watershed-based
grain separation, labeling, visualization, and export of segmented grains.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy import ndimage as ndi

from skimage import io, color, exposure, filters, morphology, measure, util
from skimage.segmentation import watershed, find_boundaries
from skimage.measure import regionprops_table


# ==========================================================
# USER CONFIGURATION
# ==========================================================

IMAGE_PATH = "data/raw/sample_image.png"
OUTPUT_DIR = "results/segmentation"

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


# ==========================================================
# AUXILIARY FUNCTIONS
# ==========================================================

def ensure_dir(path):
    """Create a directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def load_image(image_path):
    """Load an image and ensure it is in RGB format."""
    img = io.imread(image_path)

    if img.ndim == 2:
        img = color.gray2rgb(img)

    if img.shape[-1] == 4:
        img = img[:, :, :3]

    return img


def preprocess_image(rgb_img):
    """
    Convert the image to grayscale, enhance contrast with CLAHE,
    and smooth it using a Gaussian filter.
    """
    gray = color.rgb2gray(rgb_img)
    gray_eq = exposure.equalize_adapthist(gray, clip_limit=CLAHE_CLIP_LIMIT)
    gray_smooth = filters.gaussian(gray_eq, sigma=GAUSSIAN_SIGMA)

    return gray, gray_eq, gray_smooth


def build_binary_mask(gray_smooth):
    """Generate a binary mask using local thresholding."""
    gray_u8 = util.img_as_ubyte(gray_smooth)

    local_thresh = filters.threshold_local(
        gray_u8,
        block_size=LOCAL_BLOCK_SIZE,
        offset=LOCAL_OFFSET
    )

    binary = gray_u8 > local_thresh
    return binary


def clean_mask(binary_mask):
    """Remove small objects, fill holes, and apply morphological filtering."""
    cleaned = morphology.remove_small_objects(
        binary_mask.astype(bool),
        min_size=MIN_OBJECT_AREA
    )

    cleaned = morphology.remove_small_holes(
        cleaned,
        area_threshold=MIN_HOLE_AREA
    )

    selem = morphology.disk(MORPH_DISK_SIZE)
    cleaned = morphology.opening(cleaned, selem)
    cleaned = morphology.closing(cleaned, selem)

    return cleaned


def generate_markers(cleaned_mask):
    """Generate internal markers using the Euclidean distance transform."""
    distance = ndi.distance_transform_edt(cleaned_mask)

    coords = morphology.local_maxima(distance)
    coords = coords & cleaned_mask

    markers, _ = ndi.label(coords)

    return distance, markers


def apply_watershed(cleaned_mask, distance, markers):
    """Apply marker-controlled watershed segmentation."""
    labels = watershed(-distance, markers, mask=cleaned_mask)
    return labels


def filter_labeled_grains(labels):
    """Filter segmented grains based on minimum and maximum area."""
    props = measure.regionprops(labels)
    filtered = np.zeros_like(labels, dtype=np.int32)

    new_id = 1

    for region in props:
        area = region.area

        if area < FINAL_MIN_AREA:
            continue

        if FINAL_MAX_AREA is not None and area > FINAL_MAX_AREA:
            continue

        filtered[labels == region.label] = new_id
        new_id += 1

    return filtered


def create_overlay(rgb_img, labels):
    """Create an overlay image with grain boundaries."""
    overlay = rgb_img.copy()
    boundaries = find_boundaries(labels > 0, mode="outer")
    overlay[boundaries] = [255, 0, 0]

    return overlay


def export_measurements(labels, output_dir):
    """Export basic morphological measurements from labeled grains."""
    props = regionprops_table(
        labels,
        properties=(
            "label",
            "area",
            "perimeter",
            "eccentricity",
            "solidity",
            "extent",
            "major_axis_length",
            "minor_axis_length",
            "equivalent_diameter",
            "centroid",
            "bbox"
        )
    )

    df = pd.DataFrame(props)

    df["circularity"] = np.where(
        df["perimeter"] > 0,
        4 * np.pi * df["area"] / (df["perimeter"] ** 2),
        np.nan
    )

    output_path = os.path.join(output_dir, "grain_measurements.csv")
    df.to_csv(output_path, index=False)

    return df


def save_outputs(rgb_img, labels, output_dir):
    """Save segmentation outputs."""
    ensure_dir(output_dir)

    overlay = create_overlay(rgb_img, labels)

    io.imsave(os.path.join(output_dir, "overlay_boundaries.png"), overlay)
    io.imsave(
        os.path.join(output_dir, "final_binary_mask.png"),
        (labels > 0).astype(np.uint8) * 255
    )
    io.imsave(
        os.path.join(output_dir, "labeled_grains.png"),
        color.label2rgb(labels, bg_label=0)
    )


def plot_processing_steps(rgb_img, gray, gray_eq, gray_smooth, binary, cleaned, distance, labels, output_dir):
    """Save a summary figure showing the main processing steps."""
    fig, axes = plt.subplots(2, 4, figsize=(18, 10))
    axes = axes.ravel()

    images = [
        (rgb_img, "Original image", None),
        (gray, "Grayscale image", "gray"),
        (gray_eq, "CLAHE enhancement", "gray"),
        (gray_smooth, "Gaussian smoothing", "gray"),
        (binary, "Initial binary mask", "gray"),
        (cleaned, "Cleaned mask", "gray"),
        (distance, "Distance transform", "magma"),
        (color.label2rgb(labels, bg_label=0), "Segmented grains", None),
    ]

    for ax, (img, title, cmap) in zip(axes, images):
        ax.imshow(img, cmap=cmap)
        ax.set_title(title)
        ax.axis("off")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "processing_steps.png"), dpi=300)
    plt.close()


# ==========================================================
# MAIN EXECUTION
# ==========================================================

def main():
    ensure_dir(OUTPUT_DIR)

    rgb_img = load_image(IMAGE_PATH)

    gray, gray_eq, gray_smooth = preprocess_image(rgb_img)
    binary = build_binary_mask(gray_smooth)
    cleaned = clean_mask(binary)

    distance, markers = generate_markers(cleaned)
    labels = apply_watershed(cleaned, distance, markers)
    labels_filtered = filter_labeled_grains(labels)

    save_outputs(rgb_img, labels_filtered, OUTPUT_DIR)
    plot_processing_steps(
        rgb_img,
        gray,
        gray_eq,
        gray_smooth,
        binary,
        cleaned,
        distance,
        labels_filtered,
        OUTPUT_DIR
    )

    df = export_measurements(labels_filtered, OUTPUT_DIR)

    print(f"Total segmented grains: {labels_filtered.max()}")
    print(f"Results saved in: {OUTPUT_DIR}")
    print(df.head())


if __name__ == "__main__":
    main()