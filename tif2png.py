"""
tif2png_converter.py

Description:
    Converts TIFF images to PNG format using raster data. Specifically designed to handle geospatial raster data,
    this script scales the pixel values of the first three bands (assuming RGB) from their 2nd to 98th percentiles
    and exports them as RGB PNG images. This is useful for visualization of multi-band satellite or aerial imagery.

Usage:
    Run the script with the following command line arguments:
    -input_folder <path_to_input_folder_with_tiff_files>
    -output_folder <path_to_output_folder_for_png_files>

Example:
    python tif2png.py -input_folder "Predict" -output_folder "PredictPNG"
"""

import glob
import os
import rasterio
from PIL import Image
import numpy as np
import argparse

def convert_tif_to_png(tif_path, png_path):
    with rasterio.open(tif_path) as src:
        bands = [src.read(i) for i in (1, 2, 3)]
        scaled_bands = []

        for band in bands:
            band = band.astype('float32')

            # Mask out the placeholder/error values typically used in geospatial rasters
            valid_mask = band > -3.40282e+38

            # Calculate percentiles only on valid data
            if np.any(valid_mask):
                p2, p98 = np.percentile(band[valid_mask], (2, 98))
            else:
                # If no valid data, skip scaling
                continue

            band = np.clip(band, p2, p98)
            band = (band - p2) / (p98 - p2) * 255

            # Apply the mask to set invalid areas to 0 (black)
            band[~valid_mask] = 0

            scaled_bands.append(band)

        if scaled_bands:  # Check if we have any bands to process
            array = np.dstack(scaled_bands).astype(np.uint8)
            image = Image.fromarray(array, 'RGB')
            image.save(png_path)

def main(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    tif_files = glob.glob(os.path.join(input_folder, '*.tif'))

    for tif_file in tif_files:
        png_file = os.path.join(output_folder, os.path.basename(tif_file).replace('.tif', '.png'))
        print(f'Converting {tif_file} to {png_file}')
        convert_tif_to_png(tif_file, png_file)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert TIFF images to PNG format.')
    parser.add_argument('-input_folder', type=str, required=True, help='Directory containing TIFF files.')
    parser.add_argument('-output_folder', type=str, required=True, help='Directory to save PNG files.')

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    main(args.input_folder, args.output_folder)
