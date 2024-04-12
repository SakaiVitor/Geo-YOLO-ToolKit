"""
raster_clipper.py

Description:
    This script clips raster images based on polygons defined in a shapefile and exports the results as new TIFF files.
    It also checks for intersections with another shapefile containing bounding boxes and exports these intersections
    as separate shapefiles. The script is useful for extracting specific areas from large raster datasets and
    for spatial analyses involving defined regions or bounding boxes.

Usage:
    Run the script with the following command line arguments:
    -raster_path <path_to_raster_file>
    -squares_shp_path <path_to_polygon_shapefile>
    -bbox_shp_path <path_to_bounding_box_shapefile>
    -output_dir <path_to_output_directory>

Example:
    python raster_clipper.py -raster_path "/path/to/raster.tif" -squares_shp_path "/path/to/squares.shp"
    -bbox_shp_path "/path/to/bbox.shp" -output_dir "/path/to/output"
"""

import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
import argparse
import os

def reproject_shapefile_to_match_raster(shapefile_gdf, raster_crs):
    return shapefile_gdf.to_crs(raster_crs)

def make_2d(geojson):
    if 'coordinates' in geojson:
        geojson['coordinates'] = [[[x, y] for x, y, *_ in ring] for ring in geojson['coordinates']]
    return geojson

def clip_raster_with_polygon(raster_path, polygon, output_path):
    with rasterio.open(raster_path) as src:
        geojson_polygon = mapping(polygon)
        geojson_polygon_2d = make_2d(geojson_polygon)
        print("2D GeoJSON Polygon:", geojson_polygon_2d)
        try:
            out_image, out_transform = mask(src, [geojson_polygon_2d], crop=True)
        except Exception as e:
            print(f"Error during masking: {e}")
            raise
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(out_image)

def main(raster_path, squares_shp_path, bbox_shp_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with rasterio.open(raster_path) as src:
        raster_crs = src.crs
    squares_gdf = gpd.read_file(squares_shp_path)
    squares_gdf = reproject_shapefile_to_match_raster(squares_gdf, raster_crs)
    bbox_gdf = gpd.read_file(bbox_shp_path)
    bbox_gdf = reproject_shapefile_to_match_raster(bbox_gdf, raster_crs)
    for index, square in squares_gdf.iterrows():
        square_raster_path = os.path.join(output_dir, f"square_{index}.tif")
        clip_raster_with_polygon(raster_path, square.geometry, square_raster_path)
        intersecting_bboxes = bbox_gdf[bbox_gdf.intersects(square.geometry)]
        bbox_output_path = os.path.join(output_dir, f"square_{index}.shp")
        intersecting_bboxes.to_file(bbox_output_path)
        print(f"Processed square {index}: {square_raster_path}, {bbox_output_path}")

def parse_arguments():
    parser = argparse.ArgumentParser(description='Clip rasters with polygons and handle bounding boxes.')
    parser.add_argument('-raster_path', type=str, required=True, help='Path to the raster file.')
    parser.add_argument('-squares_shp_path', type=str, required=True, help='Path to the polygon shapefile for clipping.')
    parser.add_argument('-bbox_shp_path', type=str, required=True, help='Path to the bounding box shapefile.')
    parser.add_argument('-output_dir', type=str, required=True, help='Path to save the output files.')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    main(args.raster_path, args.squares_shp_path, args.bbox_shp_path, args.output_dir)
