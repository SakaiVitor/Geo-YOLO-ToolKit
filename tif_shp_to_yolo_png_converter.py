"""
tif_shp_to_yolo_png_converter.py

Description:
    This script automates the conversion of geospatial TIFF images to PNG format and transforms associated
    shapefiles into YOLO format annotations (text files). It is designed to facilitate the use of geospatial
    raster and vector data for machine learning applications, particularly those involving object detection
    models like YOLO.

Usage:
    Run the script with the following command line arguments:
    -tif_dir <path_to_directory_with_tiff_files>
    -shp_dir <path_to_directory_with_shapefiles>
    -output_base_dir <base_output_directory>

Example:
    python tif_shp_to_yolo_png_converter.py -tif_dir "path/to/tif" -shp_dir "path/to/shp" -output_base_dir "path/to/output"
"""

import os
import geopandas as gpd
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
            p2, p98 = np.percentile(band, (2, 98))
            band = np.clip(band, p2, p98)
            band = (band - p2) / (p98 - p2) * 255
            scaled_bands.append(band)
        array = np.dstack(scaled_bands).astype(np.uint8)
        image = Image.fromarray(array, 'RGB')
        image.save(png_path)

def convert_geo_to_pixel_coords(geo_coords, transform):
    minx, miny, maxx, maxy = geo_coords
    px_minx, px_miny = ~transform * (minx, miny)
    px_maxx, px_maxy = ~transform * (maxx, maxy)
    return px_minx, px_maxy, px_maxx, px_miny

def shp_to_yolo(tif_path, shp_path, yolo_path):
    gdf = gpd.read_file(shp_path)
    with rasterio.open(tif_path) as src:
        transform = src.transform
        img_width, img_height = src.width, src.height
    with open(yolo_path, 'w') as file:
        for _, row in gdf.iterrows():
            geo_bounds = row['geometry'].bounds
            px_minx, px_miny, px_maxx, px_maxy = convert_geo_to_pixel_coords(geo_bounds, transform)
            x_center = (px_minx + px_maxx) / 2.0
            y_center = (px_miny + px_maxy) / 2.0
            width = px_maxx - px_minx
            height = px_maxy - px_miny
            x_center_norm = x_center / img_width
            y_center_norm = y_center / img_height
            width_norm = width / img_width
            height_norm = height / img_height
            file.write(f"0 {x_center_norm} {y_center_norm} {width_norm} {height_norm}\n")

def main(tif_dir, shp_dir, output_base_dir):
    output_png_dir = os.path.join(output_base_dir, 'images')
    output_txt_dir = os.path.join(output_base_dir, 'labels')
    os.makedirs(output_png_dir, exist_ok=True)
    os.makedirs(output_txt_dir, exist_ok=True)
    for filename in os.listdir(tif_dir):
        if filename.endswith('.tif'):
            base_name = os.path.splitext(filename)[0]
            tif_path = os.path.join(tif_dir, filename)
            shp_path = os.path.join(shp_dir, f"{base_name}.shp")
            png_path = os.path.join(output_png_dir, f"{base_name}.png")
            yolo_path = os.path.join(output_txt_dir, f"{base_name}.txt")
            convert_tif_to_png(tif_path, png_path)
            shp_to_yolo(tif_path, shp_path, yolo_path)
            print(f"Processed and saved: {png_path}, {yolo_path}")

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert TIFF images to PNG and shapefiles to YOLO format.')
    parser.add_argument('-tif_dir', type=str, required=True, help='Directory containing TIFF files.')
    parser.add_argument('-shp_dir', type=str, required=True, help='Directory containing shapefiles.')
    parser.add_argument('-output_base_dir', type=str, required=True, help='Base directory for output files.')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    main(args.tif_dir, args.shp_dir, args.output_base_dir)
