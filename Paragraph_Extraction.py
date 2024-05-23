# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 19:08:56 2023

@author: wong zhao xuan
"""

import numpy as np
import cv2
from matplotlib import pyplot as plt
import os

def extract_paragraphs(img_path):
    img = cv2.imread(img_path, 0)

    # Calculate row projection by summing black pixels along horizontal axis
    row_projection = np.sum(img == 0, axis=1)

    # Check for the presence of a table before column projection
    if np.max(row_projection) > 500:
        # Find the indices of rows where a table is detected
        table_start = np.where(row_projection > 500)[0][0]
        table_end = np.where(row_projection > 500)[0][-1]
        
        # Remove the table section from the image
        img = np.delete(img, np.s_[table_start - 20: table_end + 20], axis=0)

    # Calculate column projection by summing black pixels along vertical axis
    column_projection = np.sum(img == 0, axis=0)

    # Finding where the column projection is greater than 0, indicating the presence of black pixels 
    column_indices = np.where(column_projection > 0)[0]

    # Calculate difference between consecutive indices 
    # identify gaps between columns
    column_diffs = np.diff(column_indices)

    # Find the gaps between columns, 65 is used as a threshold
    column_gaps = np.where(column_diffs > 30)[0]

    # Segment the image into columns using identified gaps
    # Each gap extracts a portion of the image between start & end indices with 
    # additional padding of 20 pixels on each side 
    columns = []   # used to store individual columns extracted from the image
    start_idx = column_indices[0]  # This is the index of the first column where black pixels are detected.
    for gap in column_gaps:
        end_idx = column_indices[gap]  # Identify where the gap starts.
        column = img[:, start_idx - 20: end_idx + 20]  # Extract a portion of the image representing the column, with some extra space on each side (20 pixels).
        columns.append(column)
        start_idx = column_indices[gap + 1]
    columns.append(img[:, start_idx - 20: column_indices[-1] + 20])

    # Iterates through each column, calculates the row projection by 
    # summing the black pixels along the horizontal axis, and plots the row histogram.
    col_count = 1
    all_paragraphs = []
    for col in columns:
        row_projection = np.sum(col == 0, axis=1)  # Form row 

        # Find indices where row projection is greater than 1
        row_indices = np.where(row_projection > 1)[0]
        
        # Calculates the differences between consecutive indices to identify significant gaps between rows.
        index_diffs = np.diff(row_indices)
       
        # Identifies significant gaps between rows based on the differences calculated earlier (here, a gap of 30 is used as a threshold).
        gaps = np.where(index_diffs > 30)[0]
       
        # Iterate through each gap, extract paragraphs using the identified gaps, and exclude tables based on the threshold condition
        start_idx = row_indices[0]
        for gap in gaps:
            end_idx = row_indices[gap]
            paragraph = col[start_idx - 20: end_idx + 20]  # need additional to make sure nothing is left out 
       
            # Detect and exclude tables
            black_pixels_per_row = np.sum(paragraph == 0, axis=1)
            if np.max(black_pixels_per_row) > 120 or start_idx - 20 < 0:  # Adjust the threshold as needed
                # Condition 1: There is no row with an excessive number of black pixels.
                # Condition 2: The adjusted starting index is too close to the beginning of the array.
                all_paragraphs.append(paragraph)
                
            # Updating the starting index for the next iteration of the loop
            start_idx = row_indices[gap + 1]   # Goes to the next paragraph
        all_paragraphs.append(col[start_idx - 20: row_indices[-1] + 20])

    return all_paragraphs

def save_paragraphs(paragraphs, img_path):
    # Extract the filename (without extension) from the image path
    filename = os.path.splitext(os.path.basename(img_path))[0]
    
    # Create output folder based on the image filename
    output_folder = os.path.join("Extracted_Paragraph", filename)
    os.makedirs(output_folder, exist_ok=True)
    
    # Save each extracted paragraph as a separate image
    for i, paragraph in enumerate(paragraphs):
        cv2.imwrite(os.path.join(output_folder, f"paragraph_{i + 1}.png"), paragraph)

# List of image paths
image_paths = ["001.png", "002.png", "003.png", "004.png", "005.png", "006.png", "007.png", "008.png"]

for img_path in image_paths:
    paragraphs = extract_paragraphs(img_path)
    save_paragraphs(paragraphs, img_path)








