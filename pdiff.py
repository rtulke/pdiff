#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Comparison Tool

The script 'pdiff' compares images based on a perceptual hash from the imagehash library.

Features:
 - Comparison of multiple images
 - Comparison of two specific images
 - Support for various image formats (JPG, PNG, BMP, GIF, TIFF, WEBP, PPM)
 - Display of percentage deviation
 - Filtering of similar images (5% or less difference)
 - Table output of results
    - Display of file size
    - Display of pixel size
    - Display of hash values (MD5, SHA256, etc.)
    - Display of comparison time per image pair
    - Display of an ID column with sequential numbering
- Generation of reports in HTML format for better visual representation
- Export formats (HTML, CSV, JSON)
- Statistical output for comparisons (performance, number of comparisons, etc.)
- Support for various hash algorithms (MD5, SHA256, etc.)

Author: Robert Tulke
Date: 2024-11-08
"""


import os
import hashlib
import argparse
import time
import json
import csv
from PIL import Image
import imagehash
import concurrent.futures
from tabulate import tabulate 

# Supported image formats
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.ppm']

# Functions to convert bytes into a human-readable format
def human_readable_size(size, decimal_places=2):
    """Convert bytes into a human-readable format (KB, MB, etc.)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:              # Units for file size
        if size < 1024.0:                                   # Size less than 1024 bytes
            return f"{size:.{decimal_places}f} {unit}"      # Return size and unit
        size /= 1024.0                                      # Divide size by 1024

# Function to calculate the hash value for a file
def calculate_hash(file_path, hash_algorithm):
    """Calculate the hash for the file at the given path using the specified hash algorithm."""
    hash_func = hashlib.new(hash_algorithm)                 # Select hash algorithm 
    with open(file_path, "rb") as f:                        # Open file in binary mode
        for byte_block in iter(lambda: f.read(4096), b""):  # Read file in blocks of 4096 bytes
            hash_func.update(byte_block)                    # Calculate hash for each block
    return hash_func.hexdigest()                            # Return hash value as hexadecimal number

# Function to determine image dimensions
def get_image_dimensions(file_path):
    """Get the dimensions (width x height) of the image."""
    with Image.open(file_path) as img:                      # Open image with Pillow
        return img.size  # Returns (width, height)          # Return image size

# Class for comparing images
class ImageComparator:
    # Constructor of the ImageComparator class
    def __init__(self, input_paths, percent=100, similar=False, output_file=None, output_format=None, show_time=False, show_table=False, show_id=False, hash_algorithm=None, show_pixel_size=False, show_file_size=False, show_stats=False):
        self.input_paths = input_paths                      # The paths to the input images    
        self.percent = percent                              # The percentage of maximum deviation that is considered identical
        self.similar = similar                              # Filters similar images (5% or less difference)
        self.output_file = output_file                      # The file path for output
        self.output_format = output_format                  # The output format (csv, html, json)
        self.show_time = show_time                          # Controls the display of comparison time
        self.show_table = show_table                        # Controls the display of results as a table
        self.show_id = show_id                              # Controls the display of the ID column
        self.hash_algorithm = hash_algorithm                # Controls the display of the hash value
        self.show_pixel_size = show_pixel_size              # Controls the display of pixel size
        self.show_file_size = show_file_size                # Controls the display of file size
        self.show_stats = show_stats                        # Controls the display of statistics
        self.max_hash_value = 64                            # The maximum hash value for the average hash, since the average_hash uses an 8x8 hash, the maximum difference is 64
        self.max_difference = self.max_hash_value * (self.percent / 100)  # Maximum difference based on the percentage

    # Function to calculate the perceptual hash
    def calculate_phash(self, image_path):
        with Image.open(image_path) as img:                 # Open image with Pillow
            return imagehash.average_hash(img)              # Calculate and return average hash for the image

    # Function to compare hashes
    def compare_hashes(self, hash1, hash2):
        """Compare two perceptual hashes."""
        return hash1 - hash2                                # Calculate and return the difference between the hashes

    # Function to compare 2 images based on the perceptual hash 
    def compare_images(self, image1, image2):
        start_time = time.time()                                        # Start time for each pair    

        hash1 = self.calculate_phash(image1)                            # Calculate perceptual hash for image 1
        hash2 = self.calculate_phash(image2)                            # Calculate perceptual hash for image 2
        
        difference = self.compare_hashes(hash1, hash2)                  # Compare hashes
        difference_percent = (difference / self.max_hash_value) * 100   # Convert difference to percentage
        is_within_percent = difference_percent <= self.percent          # Check if the difference is within the allowed percentage

        end_time = time.time()                                          # End time for each pair
        comparison_time = end_time - start_time                         # Calculate comparison time from start and end time
        
        return (image1, image2, difference_percent, is_within_percent, comparison_time) # Return results: image 1, image 2, difference, percentage, comparison time

    # Function to compare multiple images
    def compare_multiple_images(self, image_list):
        image_pairs = [(image_list[i], image_list[j]) for i in range(len(image_list)) for j in range(i + 1, len(image_list))] # Create image pairs from the list of images
       
        all_differences = [] # Create list for all differences 
        
        
        with concurrent.futures.ThreadPoolExecutor() as executor:                                           # Multithreading for parallel execution
            futures = [executor.submit(self.compare_images, pair[0], pair[1]) for pair in image_pairs]      # Execute comparison for each image pair
            
            for future in concurrent.futures.as_completed(futures):                                         # Process results as they become available
                image1, image2, difference_percent, is_within_percent, comparison_time = future.result()    # Retrieve results
                if is_within_percent:                                                                       # Only add results that are within the allowed percentage
                    all_differences.append({                                                                # Add results
                        "image1": image1,   
                        "image2": image2, 
                        "difference": difference_percent,                                                   # Difference in percentage
                        "comparison_time": comparison_time,                                                 # Comparison time
                    })
        
        all_differences.sort(key=lambda x: x['difference'])                                                 # Sort results by difference   
        
        return all_differences                                                                              # Return results                      

    # Function to check if the file is a supported image format
    def is_supported_image(self, file_path):
        return any(file_path.lower().endswith(ext) for ext in SUPPORTED_FORMATS)                            # Check if the file extension is in the list of supported formats

    # Function to determine the file size
    def get_image_size(self, file_path):
        return human_readable_size(os.path.getsize(file_path))                                              # Convert file size to a human-readable format

    # Function to generate the table data
    def generate_table_data(self, all_differences):
        table_data = []                                                                                     # Create table for the data                    
        headers = []                                                                                        # Create header for the table    

        # Add column headers if --id is specified
        if self.show_id:
            headers.append("ID")

        headers.extend(["Image 1", "Image 2", "Difference (%)"])    # Add column headers 

        # Add file size if --file-size is specified (per image)
        if self.show_file_size:
            headers.append("Image 1 Size")
            headers.append("Image 2 Size")

        # Add pixel size if --pixel-size is specified (per image)
        if self.show_pixel_size:
            headers.append("Image 1 Dimensions")
            headers.append("Image 2 Dimensions")

        # Add hash values if --hash is specified (per image)
        if self.hash_algorithm:
            headers.append(f"Image 1 {self.hash_algorithm.upper()} Hash")
            headers.append(f"Image 2 {self.hash_algorithm.upper()} Hash")

        # Add comparison time if --time is specified
        if self.show_time:
            headers.append("Comparison Time")

        # Generate table data
        for index, diff in enumerate(all_differences, start=1):
            row = []

            # Add ID if --id is specified
            if self.show_id:
                row.append(index)

            # Add image names, extract filename, add difference in percentage (per image)
            image1_name = os.path.basename(diff['image1'])
            image2_name = os.path.basename(diff['image2'])
            
            row.extend([
                image1_name,
                image2_name,
                f"{diff['difference']:.2f}%"
            ])

            # Add file size if --file-size is specified (per image)
            if self.show_file_size:
                image1_size = self.get_image_size(diff['image1'])
                image2_size = self.get_image_size(diff['image2'])
                row.append(image1_size)
                row.append(image2_size)

            # Add pixel size if --pixel-size is specified (per image)
            if self.show_pixel_size:
                image1_dimensions = f"{get_image_dimensions(diff['image1'])[0]}x{get_image_dimensions(diff['image1'])[1]} px"
                image2_dimensions = f"{get_image_dimensions(diff['image2'])[0]}x{get_image_dimensions(diff['image2'])[1]} px"
                row.append(image1_dimensions)
                row.append(image2_dimensions)

            # Add hash values if --hash is specified (per image)
            if self.hash_algorithm:
                image1_hash = calculate_hash(diff['image1'], self.hash_algorithm)
                image2_hash = calculate_hash(diff['image2'], self.hash_algorithm)
                row.append(image1_hash)
                row.append(image2_hash)

            # Add calculation time if --time is specified (per image pair)
            if self.show_time:
                row.append(f"{diff['comparison_time']:.4f} seconds")

            table_data.append(row) # Add row to the table 

        return headers, table_data # Return header and table data

    # Function to filter similar images (5% or less difference) if -s or --similar is specified
    def filter_similar_images(self, all_differences):
        if self.similar:
            return [diff for diff in all_differences if diff['difference'] <= 5.0]
        return all_differences

    # Function to output the differences in the console as a text table, if -t is used, or as a simple output, if not.
    def print_differences(self, all_differences):
        if not all_differences:
            print(f"No images found that match the specified deviation of {self.percent}%.")
            return

        # Apply filter for similar images if -s is used
        all_differences = self.filter_similar_images(all_differences)

        # Create the header and table data
        headers, table_data = self.generate_table_data(all_differences)

        # Table output if -t is used
        if self.show_table:
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            # Simple output of differences
            for index, diff in enumerate(all_differences, start=1):
                output = ""

                # Add ID column if --id is used
                if self.show_id:
                    output += f"ID: {index}, "

                # Display image names per image pair
                output += f"Image 1: {os.path.basename(diff['image1'])}, Image 2: {os.path.basename(diff['image2'])}, "

                # Display difference in percentage
                output += f"Difference: {diff['difference']:.2f}%"

                # Display comparison time if --time is used
                if self.show_time:
                    output += f", Comparison time: {diff['comparison_time']:.4f} seconds"

                # Display hash value if --hash is used
                if self.hash_algorithm:
                    image1_hash = calculate_hash(diff['image1'], self.hash_algorithm)
                    image2_hash = calculate_hash(diff['image2'], self.hash_algorithm)
                    output += f", Image 1 {self.hash_algorithm.upper()} Hash: {image1_hash}, Image 2 {self.hash_algorithm.upper()} Hash: {image2_hash}"

                # Display pixel size if --pixel-size (-P) is used
                if self.show_pixel_size:
                    image1_dimensions = f"{get_image_dimensions(diff['image1'])[0]}x{get_image_dimensions(diff['image1'])[1]} px"
                    image2_dimensions = f"{get_image_dimensions(diff['image2'])[0]}x{get_image_dimensions(diff['image2'])[1]} px"
                    output += f", Image 1 Dimensions: {image1_dimensions}, Image 2 Dimensions: {image2_dimensions}"

                # Display file size if --file-size (-F) is used
                if self.show_file_size:
                    image1_size = self.get_image_size(diff['image1'])
                    image2_size = self.get_image_size(diff['image2'])
                    output += f", Image 1 Size: {image1_size}, Image 2 Size: {image2_size}"

                print(output)

    # Function to generate an HTML report using the tabulate module
    def generate_html_report(self, all_differences):
        headers, table_data = self.generate_table_data(all_differences) # Generate header and table data

        # Determine the image directory based on the input options to calculate the relative paths
        if len(self.input_paths) == 1 and os.path.isdir(self.input_paths[0]):   # Directory mode
            image_directory = self.input_paths[0]                               # Set image directory    
        else:
            image_directory = os.path.dirname(self.input_paths[0])              # 2-image mode, set image directory

        # Update the table data with image tags instead of filenames
        updated_table_data = [] # Create updated table data
        for row in table_data:  # For each row in the table data
            updated_row = []

            # Add ID column if --id is specified
            if self.show_id:
                id_column = row[0]
                image1_name = str(row[1])
                image2_name = str(row[2])
            else:
                # ID column not present
                image1_name = str(row[0])
                image2_name = str(row[1])

            # Create image paths for image 1 and image 2
            image1_path = os.path.join(image_directory, image1_name)
            image2_path = os.path.join(image_directory, image2_name)

            relative_image1_path = os.path.relpath(image1_path, os.path.dirname(self.output_file))
            relative_image2_path = os.path.relpath(image2_path, os.path.dirname(self.output_file))

            # Create image tags for image 1 and image 2 and add image names - max width 200px, rounded corners 8px 
            image1_tag = f"<img src='{relative_image1_path}' alt='Image 1' style='max-width: 200px; border-radius: 8px;'><br><small>{image1_name}</small>"
            image2_tag = f"<img src='{relative_image2_path}' alt='Image 2' style='max-width: 200px; border-radius: 8px;'><br><small>{image2_name}</small>"

            # Add ID column if --id is specified
            if self.show_id:
                updated_row.append(id_column) 

            updated_row.extend([image1_tag, image2_tag] + row[3:] if self.show_id else [image1_tag, image2_tag] + row[2:])  # Maintain column order
            updated_table_data.append(updated_row)

        # Create HTML content for the report, and the table with the updated data otherwise no data available
        if not updated_table_data:
            print("No data available for HTML report.")
            return

        # Define HTML header and style
        html_content = f"""
        <html>
        <head>
            <title>Image Comparison Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; font-size: 10px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; border: 1px solid #ddd; text-align: center; }}
                th {{ background-color: #4CAF50; color: white; }}
                img {{ border-radius: 15px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); }}
                small {{ display: block; margin-top: 5px; font-size: 10px; color: #555; }}  /* Style for image captions */
                p {{ margin-top: 5px; font-size: 10px; color: #555; }}
                h1 {{ font-size: 20px; }}  /* Set font size for the heading */
            </style>
        </head>
        <body>
            <h1>Image Comparison Report</h1>
            <table>
                {tabulate(updated_table_data, headers=headers, tablefmt="unsafehtml")}
            </table>
        </body>
        </html>
        """

        # Write HTML file
        with open(self.output_file, 'w') as f:
            f.write(html_content)

        print(f"HTML report generated: {self.output_file}")

    # Function to generate a CSV report
    def generate_csv_report(self, all_differences):
        # Apply filter for similar images if -s is used
        filtered_differences = self.filter_similar_images(all_differences)

        headers, table_data = self.generate_table_data(filtered_differences)

        # Write the CSV file
        with open(self.output_file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(headers)  
            csv_writer.writerows(table_data)

        print(f"CSV report generated: {self.output_file}")

    # Function to generate a JSON report
    def generate_json_report(self, all_differences):
        """Generate a JSON report."""
        # Apply filter for similar images if -s is used
        filtered_differences = self.filter_similar_images(all_differences)

        headers, table_data = self.generate_table_data(filtered_differences)
        json_data = [dict(zip(headers, row)) for row in table_data] 

        # Write the JSON file
        with open(self.output_file, 'w') as jsonfile:
            json.dump(json_data, jsonfile, indent=4)

        print(f"JSON report generated: {self.output_file}")

    # Function to output statistics about the comparisons
    def print_stats(self, total_comparison_time, num_comparisons):
        """Print statistics about the comparisons."""
        if num_comparisons > 0:
            avg_time = total_comparison_time / num_comparisons
            print(f"\n--- Statistics ---")
            print(f"Total time for comparing all images: {total_comparison_time:.4f} seconds")
            print(f"Average time per comparison: {avg_time:.4f} seconds")
            print(f"Total number of comparisons: {num_comparisons}")
        else:
            print("\nNo comparisons made.")

    # Function to process the inputs and execute the image comparisons
    def process(self):
        total_comparison_time = 0.0 # Total comparison time for all images initial value
        num_comparisons = 0         # Number of comparisons initial value

        # Check if the input is a directory or two specific image files
        if len(self.input_paths) == 1:
 
            # Directory mode
            directory = self.input_paths[0]
            if not os.path.isdir(directory):
                print(f"The directory '{directory}' does not exist.")
                return

            # Create list of image files in the directory
            image_list = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and self.is_supported_image(f)]

            # Error message if no supported image files were found
            if not image_list:
                print(f"No supported image files found in directory '{directory}'.")
                return

            all_differences = self.compare_multiple_images(image_list) # Perform comparison of multiple images

            # Calculate total comparison time and number of comparisons
            total_comparison_time = sum(diff['comparison_time'] for diff in all_differences)
            num_comparisons = len(all_differences)

            # Output differences in the console
            self.print_differences(all_differences)

            # Generate report based on the selected output format
            if self.output_file and self.output_format == 'html':
                self.generate_html_report(all_differences)
            elif self.output_file and self.output_format == 'csv':
                self.generate_csv_report(all_differences)
            elif self.output_file and self.output_format == 'json':
                self.generate_json_report(all_differences)

        # Two-image mode
        elif len(self.input_paths) == 2:

            image1, image2 = self.input_paths

            # Error message if one or both of the specified files are not supported image files
            if not (self.is_supported_image(image1) and self.is_supported_image(image2)):
                print(f"One or both of the specified files are not supported image files.")
                return

            # Perform image comparison
            image1, image2, difference_percent, is_within_percent, comparison_time = self.compare_images(image1, image2)

            # Output differences in the console and generate report based on the selected output format
            if is_within_percent:
                output = f"'{image1}' and '{image2}' are within the specified deviation (Difference: {difference_percent:.2f}%)"
                if self.show_time:
                    output += f", Comparison time: {comparison_time:.4f} seconds"
                print(output)

        
                total_comparison_time = comparison_time
                num_comparisons = 1
                
                # Generate report based on the selected output format
                if self.output_file and self.output_format == 'html':
                    self.generate_html_report([{
                        "image1": image1,
                        "image2": image2,
                        "difference": difference_percent,
                        "comparison_time": comparison_time,
                    }])
                elif self.output_file and self.output_format == 'csv':
                    self.generate_csv_report([{
                        "image1": image1,
                        "image2": image2,
                        "difference": difference_percent,
                        "comparison_time": comparison_time,
                    }])
                elif self.output_file and self.output_format == 'json':
                    self.generate_json_report([{
                        "image1": image1,
                        "image2": image2,
                        "difference": difference_percent,
                        "comparison_time": comparison_time,
                    }])

        # Output statistics if --stats is used
        if self.show_stats:
            self.print_stats(total_comparison_time, num_comparisons)

# Main function to run the script
def main():
    # Process parameters and arguments
    parser = argparse.ArgumentParser(description="Compare images in a directory or two specific image files using hashes.")
    parser.add_argument('-i', '--input', type=str, nargs='+', required=True, help='Path to a directory or to two image files')
    parser.add_argument('-p', '--percent', type=int, default=100, help='Percentage of maximum deviation that is considered identical (e.g., -p 80 means 20%% deviation allowed)')
    parser.add_argument('-s', '--similar', action='store_true', help='Only print images with up to 5%% difference')
    parser.add_argument('-o', '--output', type=str, nargs=2, help='Output format and file, e.g., "-o html output.html" or "-o csv output.csv" or "-o json output.json"')
    parser.add_argument('-T', '--time', action='store_true', help='Display comparison time for each image pair')
    parser.add_argument('-t', '--table', action='store_true', help='Display comparison results as a text table')
    parser.add_argument('-N', '--id', action='store_true', help='Add an ID column with a running number')
    parser.add_argument('-H', '--hash', type=str, help='Display hash for the specified algorithm (e.g., sha256, md5, etc.)')
    parser.add_argument('-P', '--pixel-size', action='store_true', help='Display image dimensions in pixels (width x height) in the table')
    parser.add_argument('-F', '--file-size', action='store_true', help='Display file size of images in the table')
    parser.add_argument('-S', '--stats', action='store_true', help='Display statistics: total time, average time per comparison, and number of comparisons')
    args = parser.parse_args()

    # Check if the specified hash algorithm is available, if --hash is used
    if args.hash and args.hash not in hashlib.algorithms_available:
        print(f"Error: The specified hash algorithm '{args.hash}' is not available in hashlib.")
        return

    # Check if the specified output format is supported
    output_format = None
    output_file = None
    if args.output:
        output_format, output_file = args.output
        if output_format not in ['html', 'csv', 'json']:
            print(f"Error: Unsupported output format '{output_format}'. Supported formats are 'html', 'csv', and 'json'.")
            return

    # Create ImageComparator object and start the comparison process
    comparator = ImageComparator(
        input_paths=args.input,             # Paths to the input images
        percent=args.percent,               # Percentage of maximum deviation
        similar=args.similar,               # Filters similar images (5% or less difference)
        output_file=output_file,            # File path for output
        output_format=output_format,        # Output format (csv, html, json)
        show_time=args.time,                # Controls the display of comparison time
        show_table=args.table,              # Controls the display of results as a table
        show_id=args.id,                    # Controls the display of the ID column
        hash_algorithm=args.hash,           # Controls the display of the hash value
        show_pixel_size=args.pixel_size,    # Controls the display of pixel size
        show_file_size=args.file_size,      # Controls the display of file size
        show_stats=args.stats               # Controls the display of statistics
    )
    comparator.process()

if __name__ == "__main__":
    main()
