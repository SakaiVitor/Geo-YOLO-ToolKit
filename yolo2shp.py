"""
yolo2shp.py

Description:
    This script converts detection outputs from YOLO format text files into geospatial shapefiles (.shp).
    It aligns detections with their corresponding TIFF images based on geographic metadata from the TIFF files.
    Accepts directories for TIFF images, YOLO detection files, and output shapefiles as command line arguments.

Usage:
    Run the script with the following command line arguments:
    -tif_dir <path_to_tiff_directory>
    -detect_dir <path_to_detection_directory>
    -output_dir <path_to_output_directory>

Example:
    python yolo2shp.py -tif_dir Predict -detect_dir detection -output_dir final_shp
"""

import os
import geopandas as gpd
import rasterio
from shapely.geometry import box
import pandas as pd
from pathlib import Path
import argparse

def detections_to_shp(tif_path, detections_path, output_path):
    with rasterio.open(tif_path) as src:
        transform = src.transform
        crs = src.crs

    detections = pd.read_csv(detections_path, sep=' ', header=None,
                             names=['class_id', 'x_center', 'y_center', 'width', 'height'])

    geoms = []
    for _, row in detections.iterrows():
        x_center, y_center, width, height = row['x_center'], row['y_center'], row['width'], row['height']
        x1 = (x_center - width / 2) * src.width
        y1 = (y_center - height / 2) * src.height
        x2 = (x_center + width / 2) * src.width
        y2 = (y_center + height / 2) * src.height
        top_left = transform * (x1, y1)
        bottom_right = transform * (x2, y2)
        geom = box(top_left[0], bottom_right[1], bottom_right[0], top_left[1])
        geoms.append(geom)

    gdf = gpd.GeoDataFrame({'geometry': geoms, 'class_id': detections['class_id']})
    gdf.crs = crs
    gdf.to_file(output_path)

def process_directory(tif_dir, detections_dir, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for detection_file in os.listdir(detections_dir):
        if detection_file.endswith('.txt'):
            base_name = os.path.splitext(detection_file)[0]
            tif_path = os.path.join(tif_dir, f"{base_name}.tif")
            detections_path = os.path.join(detections_dir, detection_file)
            output_path = os.path.join(output_dir, f"{base_name}.shp")
            if os.path.exists(tif_path):
                print(f"Processing {base_name}")
                detections_to_shp(tif_path, detections_path, output_path)
            else:
                print(f"Warning: No matching TIF file found for {detection_file}")

def main():
    parser = argparse.ArgumentParser(description='Convert YOLO detection outputs to Shapefiles.')
    parser.add_argument('-tif_dir', type=str, required=True, help='Directory containing TIFF files.')
    parser.add_argument('-detect_dir', type=str, required=True, help='Directory containing detection TXT files.')
    parser.add_argument('-output_dir', type=str, required=True, help='Directory to output the Shapefiles.')

    args = parser.parse_args()

    process_directory(args.tif_dir, args.detect_dir, args.output_dir)

if __name__ == '__main__':
    main()
