"""
Image processing module with quality optimization features.
Handles image loading, resizing, sharpening, and ICC profile preservation.
"""

from PIL import Image, ImageFilter
from pathlib import Path
from typing import Tuple, List, Optional


class ImageProcessor:
    """
    Advanced image processor with quality-focused features:
    - LANCZOS resampling for best quality
    - Conditional sharpening for small icons
    - ICC color profile preservation
    - Optimized PNG compression
    """

    # Sharpening thresholds and parameters
    SHARPEN_THRESHOLD = 128  # Apply sharpening to icons smaller than this

    # Size-specific sharpening parameters (size range: (radius, percent, threshold))
    SHARPEN_PARAMS = {
        (0, 32): (0.6, 70, 3),      # Very small icons: aggressive sharpening
        (33, 64): (0.5, 50, 3),     # Small icons: moderate sharpening
        (65, 127): (0.4, 35, 3),    # Medium icons: light sharpening
    }

    def __init__(self):
        """Initialize the image processor."""
        self.icc_profile = None

    def load_image(self, path: str) -> Image.Image:
        """
        Load an image and prepare it for processing.

        Args:
            path: Path to the image file

        Returns:
            PIL Image object in RGBA mode

        Raises:
            Exception: If image cannot be loaded
        """
        try:
            img = Image.open(path)

            # Preserve ICC profile if present
            self.icc_profile = img.info.get('icc_profile')

            # Convert to RGBA to preserve transparency
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            return img

        except Exception as e:
            raise Exception(f"Could not load image: {str(e)}")

    def resize_with_quality(self, img: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """
        Resize image with maximum quality using LANCZOS resampling.
        Applies conditional sharpening for small icons.

        Args:
            img: Source image in RGBA mode
            size: Target size as (width, height) tuple

        Returns:
            Resized (and possibly sharpened) image
        """
        width, height = size

        # Resize with high-quality LANCZOS filter
        resized = img.resize((width, height), Image.Resampling.LANCZOS)

        # Apply sharpening for small icons to compensate for downsampling blur
        max_dimension = max(width, height)
        if max_dimension < self.SHARPEN_THRESHOLD:
            resized = self._apply_sharpening(resized, max_dimension)

        return resized

    def _apply_sharpening(self, img: Image.Image, size: int) -> Image.Image:
        """
        Apply size-appropriate sharpening to compensate for downsampling blur.

        Args:
            img: Image to sharpen
            size: Maximum dimension of the image

        Returns:
            Sharpened image
        """
        # Find appropriate sharpening parameters based on size
        radius, percent, threshold = 0.5, 50, 3  # Default params

        for (min_size, max_size), params in self.SHARPEN_PARAMS.items():
            if min_size <= size <= max_size:
                radius, percent, threshold = params
                break

        # Apply unsharp mask filter
        try:
            sharpened = img.filter(
                ImageFilter.UnsharpMask(
                    radius=radius,
                    percent=percent,
                    threshold=threshold
                )
            )
            return sharpened
        except Exception:
            # If sharpening fails, return original
            return img

    def save_png_optimized(self, img: Image.Image, path: Path) -> None:
        """
        Save image as optimized PNG with maximum compression.
        Preserves ICC profile if available.

        Args:
            img: Image to save
            path: Output file path
        """
        save_kwargs = {
            "format": "PNG",
            "optimize": True,        # Enable PNG optimization
            "compress_level": 9,     # Maximum compression (0-9)
        }

        # Preserve ICC profile if we extracted one
        if self.icc_profile:
            save_kwargs["icc_profile"] = self.icc_profile

        img.save(path, **save_kwargs)

    def save_ico_multisize(self, images: List[Image.Image], path: Path) -> None:
        """
        Save multiple images as a single multisize ICO file.

        Args:
            images: List of images in descending size order
            path: Output ICO file path
        """
        if len(images) == 0:
            raise ValueError("No images provided for ICO generation")

        # ICO format requires images in descending size order
        # The first image should be the largest
        if len(images) > 1:
            images[0].save(
                path,
                format="ICO",
                append_images=images[1:]
            )
        else:
            images[0].save(path, format="ICO")

    def generate_png_icon(self, source_img: Image.Image, size: Tuple[int, int],
                         output_path: Path) -> None:
        """
        Complete workflow: resize with quality and save as optimized PNG.

        Args:
            source_img: Source image in RGBA mode
            size: Target size as (width, height)
            output_path: Where to save the PNG file
        """
        resized = self.resize_with_quality(source_img, size)
        self.save_png_optimized(resized, output_path)

    def generate_ico_from_source(self, source_img: Image.Image,
                                 sizes: List[int], output_path: Path) -> List[Image.Image]:
        """
        Generate multisize ICO from source image.

        Args:
            source_img: Source image in RGBA mode
            sizes: List of square sizes (e.g., [16, 32, 48, ...])
            output_path: Where to save the ICO file

        Returns:
            List of resized images that were saved
        """
        # Sort sizes in descending order for ICO format
        sizes_sorted = sorted(sizes, reverse=True)

        # Resize all variations with quality settings
        icon_images = []
        for size in sizes_sorted:
            resized = self.resize_with_quality(source_img, (size, size))
            icon_images.append(resized)

        # Save as multisize ICO
        self.save_ico_multisize(icon_images, output_path)

        return icon_images
