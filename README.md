### GEO-YOLO-ToolKit ###
Geospatial Image Processing Toolkit

This toolkit comprises a set of Python scripts designed to facilitate the processing of geospatial raster and vector data for applications such as machine learning in computer vision and object detection. Each script is tailored for specific tasks including image conversion, image segmentation, bounding box visualization, and more.

Scripts and Usage

### 1. yolo2shp.py
Description: Converts detection outputs from YOLO format text files into geospatial shapefiles (.shp). It aligns detections with their corresponding TIFF images based on geographic metadata from the TIFF files.
Usage:
```bash
python yolo2shp.py -tif_dir <path_to_tiff_directory> -detect_dir <path_to_detection_directory> -output_dir <path_to_output_directory>
```

### 2. tif2png_converter.py
Description: Converts TIFF images to PNG format using raster data, specifically handling multi-band geospatial rasters by applying a percentile stretch to improve visualization.
Usage:
```bash
python tif2png_converter.py -input_folder <path_to_input_folder> -output_folder <path_to_output_folder>
```

### 3. group_bbox_creator.py
Description: Processes shapefiles to create grouped axis-aligned bounding boxes based on a specified attribute field, useful for spatial analyses and reducing complex vector data into simpler bounding rectangles.
Usage:
```bash
python group_bbox_creator.py -input_folder <input_shapefile_folder> -output_folder <output_folder> -group_field <field_name>
```

### 4. tif_shp_to_yolo_png_converter.py
Description: Automates the conversion of geospatial TIFF images to PNG format and transforms associated shapefiles into YOLO format annotations, facilitating the use of raster and vector data for machine learning model training.
Usage:
```bash
python tif_shp_to_yolo_png_converter.py -tif_dir <tif_directory> -shp_dir <shapefile_directory> -output_base_dir <output_directory>
```

### 5. raster_clipper.py
Description: Clips raster images based on polygons defined in a shapefile and exports the results as new TIFF files. Additionally, it checks intersections with another shapefile containing bounding boxes and exports these intersections as separate shapefiles.
Usage:
```bash
python raster_clipper.py -raster_path <path_to_raster> -squares_shp_path <path_to_polygon_shapefile> -bbox_shp_path <path_to_bounding_box_shapefile> -output_dir <output_directory>
```

### 6. tif_to_png_squares.py
Description: Converts TIFF images to PNG format and splits these PNGs into smaller square segments. This script is particularly useful for preparing data for machine learning tasks in computer vision by creating manageable, uniform image sizes.
Usage:
```bash
python tif_to_png_squares.py -input_folder <input_folder> -temp_output_folder <temporary_png_folder> -final_output_folder <final_square_segments_folder> -square_size <size_of_each_square>
```

### 7. draw_bboxes.py
Description: Draws bounding boxes on images based on annotations in YOLO format. This is useful for visualizing the coverage and accuracy of object detection models directly on the images.
Usage:
```bash
python draw_bboxes.py -image_path <path_to_image> -label_path <path_to_label_file> -output_path <path_to_output_image>
```

### Installation

1. Clone this repository to your local machine.
2. Ensure you have Python 3.6+ installed.
3. Install required dependencies:
   pip install pillow rasterio geopandas numpy
4. Navigate to the script directory and run the desired script as shown in the usage section above.
