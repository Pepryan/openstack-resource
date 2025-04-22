import os
import json
import re
import pandas as pd
import config
from utils.format_utils import Formatter

def read_json_file(file_path, default=None):
    """
    Read JSON file
    
    Args:
        file_path (str): Path to JSON file
        default (any): Default value if file doesn't exist or is invalid
        
    Returns:
        dict: JSON data
    """
    if default is None:
        default = {}
        
    if not os.path.exists(file_path):
        return default
        
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        return default

def write_json_file(file_path, data, indent=4):
    """
    Write JSON file
    
    Args:
        file_path (str): Path to JSON file
        data (dict): Data to write
        indent (int): Indentation level
    """
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=indent)

def get_file_last_updated(file_path):
    """
    Get file last updated timestamp
    
    Args:
        file_path (str): Path to file
        
    Returns:
        str: Formatted timestamp
    """
    timestamp = os.path.getmtime(file_path)
    return Formatter.format_timestamp(timestamp)

def read_reserved_data():
    """
    Read reserved data from JSON file
    
    Returns:
        dict: Reserved data
    """
    return read_json_file(config.RESERVED_FILE_PATH)

def update_or_add_reserved_data(data, compute_name, cpu, ram, kebutuhan):
    """
    Update or add reserved data
    
    Args:
        data (dict): Reserved data
        compute_name (str): Compute name
        cpu (str): CPU value
        ram (str): RAM value
        kebutuhan (str): Kebutuhan value
    """
    if compute_name not in data:
        data[compute_name] = {}
    if cpu:
        data[compute_name]['CPU'] = cpu
    if ram:
        data[compute_name]['RAM'] = ram
    if kebutuhan:
        data[compute_name]['Kebutuhan'] = kebutuhan

def get_sorted_computes():
    """
    Get sorted list of compute hosts
    
    Returns:
        list: Sorted list of compute hosts
    """
    with open(config.RATIO_FILE_PATH, 'r') as file:
        lines = file.readlines()
        compute_names = [line.split(',')[0].strip() for line in lines]
    return sorted(compute_names)

def extract_cephdf_data():
    """
    Extract data from cephdf.txt
    
    Returns:
        dict: Extracted data
    """
    # Initialize variables to store the extracted values
    total = avail = raw_used = raw_used_percentage = "N/A"

    # Open the file and read it line by line
    with open(config.CEPHDF_FILE_PATH, "r") as file:
        lines = file.readlines()

        # Initialize a section flag
        in_raw_storage_section = False

        for line in lines:
            # Check if the line starts with "RAW STORAGE" to identify the section
            if line.startswith("--- RAW STORAGE ---"):
                in_raw_storage_section = True
                continue
            elif line.startswith("--- POOLS ---"):
                in_raw_storage_section = False
                continue

            # Process lines in the "RAW STORAGE" section
            if in_raw_storage_section:
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) == 6 and parts[0] == "TOTAL":
                    total = parts[1]
                    avail = parts[2]
                    raw_used = parts[3]
                    raw_used_percentage = parts[5]

    # Return the extracted values as a dictionary
    return {
        "Total": total,
        "Avail": avail,
        "Raw Used": raw_used,
        "%Raw Used": raw_used_percentage
    }
