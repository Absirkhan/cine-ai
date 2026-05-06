"""
Image and Video Filters using OpenCV
Provides visual editing capabilities
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import cv2
import numpy as np
from typing import Optional


class ImageFilters:
    """Collection of image/video filters using OpenCV"""

    @staticmethod
    def darken(image_path: str, output_path: str, amount: float = 0.3) -> str:
        """
        Darken an image

        Args:
            image_path: Input image path
            output_path: Output image path
            amount: Darkening amount (0.0 to 1.0)

        Returns:
            Path to output image
        """
        img = cv2.imread(image_path)
        darkened = cv2.convertScaleAbs(img, alpha=(1 - amount), beta=0)
        cv2.imwrite(output_path, darkened)
        return output_path

    @staticmethod
    def brighten(image_path: str, output_path: str, amount: float = 0.3) -> str:
        """Brighten an image"""
        img = cv2.imread(image_path)
        brightened = cv2.convertScaleAbs(img, alpha=(1 + amount), beta=0)
        cv2.imwrite(output_path, brightened)
        return output_path

    @staticmethod
    def adjust_contrast(image_path: str, output_path: str, amount: float = 1.5) -> str:
        """Adjust image contrast"""
        img = cv2.imread(image_path)
        adjusted = cv2.convertScaleAbs(img, alpha=amount, beta=0)
        cv2.imwrite(output_path, adjusted)
        return output_path

    @staticmethod
    def adjust_saturation(image_path: str, output_path: str, amount: float = 1.5) -> str:
        """Adjust color saturation"""
        img = cv2.imread(image_path)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)

        # Adjust saturation channel
        hsv[:, :, 1] = hsv[:, :, 1] * amount
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)

        adjusted = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        cv2.imwrite(output_path, adjusted)
        return output_path

    @staticmethod
    def apply_blur(image_path: str, output_path: str, amount: int = 15) -> str:
        """Apply Gaussian blur"""
        img = cv2.imread(image_path)
        # Ensure kernel size is odd
        kernel_size = amount if amount % 2 == 1 else amount + 1
        blurred = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
        cv2.imwrite(output_path, blurred)
        return output_path

    @staticmethod
    def apply_sharpen(image_path: str, output_path: str) -> str:
        """Sharpen image"""
        img = cv2.imread(image_path)

        # Sharpening kernel
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])

        sharpened = cv2.filter2D(img, -1, kernel)
        cv2.imwrite(output_path, sharpened)
        return output_path

    @staticmethod
    def to_grayscale(image_path: str, output_path: str) -> str:
        """Convert to grayscale"""
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Convert back to BGR for consistency
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        cv2.imwrite(output_path, gray_bgr)
        return output_path

    @staticmethod
    def apply_sepia(image_path: str, output_path: str) -> str:
        """Apply sepia tone filter"""
        img = cv2.imread(image_path).astype(np.float32)

        # Sepia transformation matrix
        sepia_matrix = np.array([[0.272, 0.534, 0.131],
                                [0.349, 0.686, 0.168],
                                [0.393, 0.769, 0.189]])

        sepia = cv2.transform(img, sepia_matrix)
        sepia = np.clip(sepia, 0, 255).astype(np.uint8)
        cv2.imwrite(output_path, sepia)
        return output_path

    @staticmethod
    def adjust_temperature(image_path: str, output_path: str, amount: float = 1.2) -> str:
        """
        Adjust color temperature (warm/cool)
        amount > 1.0 = warmer (more red/orange)
        amount < 1.0 = cooler (more blue)
        """
        img = cv2.imread(image_path).astype(np.float32)

        if amount > 1.0:
            # Warm: increase red/yellow
            img[:, :, 2] = np.clip(img[:, :, 2] * amount, 0, 255)  # Red
            img[:, :, 1] = np.clip(img[:, :, 1] * (1 + (amount - 1) * 0.5), 0, 255)  # Green
        else:
            # Cool: increase blue
            img[:, :, 0] = np.clip(img[:, :, 0] * (2 - amount), 0, 255)  # Blue

        cv2.imwrite(output_path, img.astype(np.uint8))
        return output_path

    @staticmethod
    def apply_vignette(image_path: str, output_path: str, amount: float = 0.5) -> str:
        """Apply vignette effect (darker edges)"""
        img = cv2.imread(image_path)
        rows, cols = img.shape[:2]

        # Create vignette mask
        X_resultant_kernel = cv2.getGaussianKernel(cols, cols * amount)
        Y_resultant_kernel = cv2.getGaussianKernel(rows, rows * amount)
        resultant_kernel = Y_resultant_kernel * X_resultant_kernel.T
        mask = resultant_kernel / resultant_kernel.max()

        # Apply mask to each channel
        vignette = np.copy(img).astype(np.float32)
        for i in range(3):
            vignette[:, :, i] = vignette[:, :, i] * mask

        cv2.imwrite(output_path, vignette.astype(np.uint8))
        return output_path
