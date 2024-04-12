"""
group_bbox_creator.py

Description:
    Processes shapefiles to create grouped axis-aligned bounding boxes based on a specified attribute field.
    Each group will be combined into a single bounding box that encompasses all features within that group.
    This is useful for spatial analyses that require simplified representation of feature extents grouped by attributes.

Usage:
    Run the script with the following command line arguments:
    -input_folder <path_to_input_folder_with_shapefiles>
    -output_folder <path_to_output_folder_for_shapefiles>
    -group_field <field_to_group_by>

Example:
    python group_bbox_creator.py -input_folder "path_to_input_folder_with_shapefiles" -output_folder "path_to_output_folder_for_shapefiles" -group_field "Id"
"""

import os
import geopandas as gpd
from shapely.geometry import box
import argparse

def create_grouped_axis_aligned_bounding_boxes(shapefile_path, output_path, group_field):
    # Load the original shapefile
    gdf = gpd.read_file(shapefile_path)

    # Group by the specified field and create a bounding box for each group
    grouped = gdf.dissolve(by=group_field)
    grouped['geometry'] = grouped.apply(lambda x: box(*x.geometry.bounds), axis=1)

    # Save the new shapefile with grouped axis-aligned bounding boxes
    grouped.reset_index().to_file(output_path, index=False)

def process_folder(input_folder, output_folder, group_field):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.shp'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            print(f"Processing {filename}...")
            create_grouped_axis_aligned_bounding_boxes(input_path, output_path, group_field)
            print(f"Output saved to {output_path}")

def parse_arguments():
    parser = argparse.ArgumentParser(description='Create grouped axis-aligned bounding boxes from shapefiles.')
    parser.add_argument('-input_folder', type=str, required=True, help='Directory containing input shapefiles.')
    parser.add_argument('-output_folder', type=str, required=True, help='Directory to save output shapefiles.')
    parser.add_argument('-group_field', type=str, required=True, help='Attribute field to group by.')

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    process_folder(args.input_folder, args.output_folder, args.group_field)
