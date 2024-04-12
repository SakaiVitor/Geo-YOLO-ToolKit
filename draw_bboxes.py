"""
draw_bboxes.py

Description:
    Draws bounding boxes on images based on annotations in YOLO format (class, x_center, y_center, width, height).
    This script is useful for visualizing the coverage and accuracy of object detection models directly on the images.

Usage:
    Run the script with the following command line arguments:
    -image_path <path_to_image_file>
    -label_path <path_to_label_file>
    -output_path <path_to_output_image_with_drawn_bboxes>

Example:
    python draw_bboxes.py -image_path "images/square_0.png" -label_path "labels/square_0.txt"
    -output_path "output_image.png"
"""

from PIL import Image, ImageDraw
import argparse

def draw_bounding_boxes(image_path, label_path, output_path):
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        width, height = img.size

        with open(label_path, 'r') as file:
            for line in file:
                class_id, x_center, y_center, w, h = map(float, line.split())
                x_center *= width
                y_center *= height
                w *= width
                h *= height
                left = x_center - (w / 2)
                top = y_center - (h / 2)
                right = x_center + (w / 2)
                bottom = y_center + (h / 2)
                draw.rectangle([left, top, right, bottom], outline="red", width=2)

        img.save(output_path)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Draw bounding boxes on images based on YOLO format annotations.')
    parser.add_argument('-image_path', type=str, required=True, help='Path to the image file.')
    parser.add_argument('-label_path', type=str, required=True, help='Path to the label file with YOLO format.')
    parser.add_argument('-output_path', type=str, required=True, help='Path where the output image will be saved.')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    draw_bounding_boxes(args.image_path, args.label_path, args.output_path)
