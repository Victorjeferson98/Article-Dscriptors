"""
02_mask_preprocessing.py

This script receives a colored segmented grain image and converts it into a
clean binary mask. It also removes border-touching grains and creates small
gaps between adjacent grains.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

from skimage.io import imread, imsave
from skimage.morphology import binary_erosion, disk
from skimage.segmentation import clear_border


# ==========================================================
# USER CONFIGURATION
# ==========================================================

IMAGE_PATH = "results/segmentation/labeled_grains.png"
OUTPUT_PATH = "results/segmentation/binary_mask_no_border_with_gaps.png"

EROSION_RADIUS = 1


# ==========================================================
# MAIN FUNCTION
# ==========================================================

def preprocess_colored_segmentation(image_path, output_path, erosion_radius=1):
    """Convert a colored segmentation image into a clean binary mask."""
    img = imread(image_path)

    if img.ndim == 2:
        raise ValueError("Expected an RGB image, but a grayscale image was found.")

    if img.shape[-1] == 4:
        img = img[..., :3]

    # Identify black background pixels.
    background = np.all(img == [0, 0, 0], axis=-1)

    # Any non-black pixel is considered part of a grain.
    grain_mask = ~background

    # Remove grains touching the image border.
    mask_no_border = clear_border(grain_mask)

    # Identify all unique non-black colors.
    pixels = img.reshape(-1, 3)
    unique_colors = np.unique(pixels, axis=0)
    unique_colors = unique_colors[np.any(unique_colors != [0, 0, 0], axis=1)]

    selem = disk(erosion_radius)
    final_binary = np.zeros(mask_no_border.shape, dtype=bool)

    # Process each color separately to create small gaps between grains.
    for grain_color in unique_colors:
        color_mask = np.all(img == grain_color, axis=-1)
        color_mask = color_mask & mask_no_border

        if np.any(color_mask):
            eroded = binary_erosion(color_mask, selem)
            final_binary |= eroded

    binary_image = (final_binary * 255).astype(np.uint8)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    imsave(output_path, binary_image)

    return img, grain_mask, mask_no_border, binary_image, unique_colors


def plot_result(img, grain_mask, mask_no_border, binary_image):
    """Show the preprocessing result."""
    fig, axes = plt.subplots(1, 4, figsize=(20, 6))

    axes[0].imshow(img)
    axes[0].set_title("Original RGB image")
    axes[0].axis("off")

    axes[1].imshow(grain_mask, cmap="gray")
    axes[1].set_title("Initial grain mask")
    axes[1].axis("off")

    axes[2].imshow(mask_no_border, cmap="gray")
    axes[2].set_title("Border grains removed")
    axes[2].axis("off")

    axes[3].imshow(binary_image, cmap="gray")
    axes[3].set_title("Final binary mask with gaps")
    axes[3].axis("off")

    plt.tight_layout()
    plt.show()


def main():
    img, grain_mask, mask_no_border, binary_image, unique_colors = preprocess_colored_segmentation(
        IMAGE_PATH,
        OUTPUT_PATH,
        EROSION_RADIUS
    )

    plot_result(img, grain_mask, mask_no_border, binary_image)

    print(f"Binary mask saved in: {OUTPUT_PATH}")
    print(f"Detected colors/grains: {len(unique_colors)}")


if __name__ == "__main__":
    main()