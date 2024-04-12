"""
tif_to_png_squares.py

Description:
    Converts geospatial TIFF images to PNG format and then splits these PNG images into smaller square segments.
    This process is useful for preparing data for machine learning tasks, especially in computer vision, by
    creating manageable, uniform image sizes from large geospatial datasets.

Usage:
    Run the script with the following command line arguments:
    -input_folder <path_to_input_folder_with_tiff_files>
    -temp_output_folder <temporary_path_for_storing_png_files>
    -final_output_folder <path_for_storing_square_segments>
    -square_size <size_of_each_square_in_pixels>

Example:
    python tif_to_png_squares.py -input_folder "Predict" -temp_output_folder "PredictPNG"
    -final_output_folder "PredictPNGSquares" -square_size 200
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
            valid_mask = band > -3.40282e+38
            if np.any(valid_mask):
                p2, p98 = np.percentile(band[valid_mask], (2, 98))
            else:
                continue
            band = np.clip(band, p2, p98)
            band = (band - p2) / (p98 - p2) * 255
            band[~valid_mask] = 0
            scaled_bands.append(band)

        if scaled_bands:
            array = np.dstack(scaled_bands).astype(np.uint8)
            image = Image.fromarray(array, 'RGB')
            image.save(png_path)

def split_png_to_squares(png_path, output_folder, square_size):
    image = Image.open(png_path)
    width, height = image.size
    num_rows = height // square_size
    num_cols = width // square_size

    base_name = os.path.splitext(os.path.basename(png_path))[0]
    squares_output_folder = os.path.join(output_folder, base_name)
    os.makedirs(squares_output_folder, exist_ok=True)

    for y in range(num_rows):
        for x in range(num_cols):
            left = x * square_size
            upper = y * square_size
            right = (x + 1) * square_size
            lower = (y + 1) * square_size
            square = image.crop((left, upper, right, lower))
            square.save(os.path.join(squares_output_folder, f"square_{y}_{x}.png"))

def main(input_folder, temp_output_folder, final_output_folder, square_size):
    os.makedirs(temp_output_folder, exist_ok=True)
    os.makedirs(final_output_folder, exist_ok=True)

    tif_files = glob.glob(os.path.join(input_folder, '*.tif'))

    for tif_file in tif_files:
        base_name = os.path.basename(tif_file)
        png_path = os.path.join(temp_output_folder, base_name.replace('.tif', '.png'))
        print(f'Converting {tif_file} to {png_path}')
        convert_tif_to_png(tif_file, png_path)
        print(f'Splitting {png_path} into squares')
        split_png_to_squares(png_path, final_output_folder, square_size)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert TIFF images to PNG and split into squares for ML training.')
    parser.add_argument('-input_folder', type=str, required=True, help='Directory containing TIFF files.')
    parser.add_argument('-temp_output_folder', type=str, required=True, help='Temporary directory for PNG files.')
    parser.add_argument('-final_output_folder', type=str, required=True, help='Directory to store final square segments.')
    parser.add_argument('-square_size', type=int, required=True, help='Size of each square segment in pixels.')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    main(args.input_folder, args.temp_output_folder, args.final_output_folder, args.square_size)
