import pandas as pd
import config
from utils.file_utils import read_reserved_data

def calculate_total_capacity_allocation_ratio(ratio, formatted_data):
    """
    Calculate total capacity for a specific allocation ratio
    
    Args:
        ratio (str): Allocation ratio (e.g., '1:1', '1:4', '1:8')
        formatted_data (list): Formatted data
        
    Returns:
        tuple: (total_capacity, total_capacity_memory)
    """
    total_capacity = 0
    total_capacity_memory = 0

    # Loop through the formatted data
    for item in formatted_data:
        vcpus_ratio = item['vCPUs Ratio']
        
        # Check if the host/compute has the matching ratio
        if vcpus_ratio == ratio:
            vcpus_capacity = item['VCPUs']['Capacity']
            total_capacity += vcpus_capacity

            memory_capacity = item['Memory']['Capacity']
            total_capacity_memory += memory_capacity

    return total_capacity, total_capacity_memory

def calculate_total_usage_allocation_ratio(ratio, formatted_data):
    """
    Calculate total usage for a specific allocation ratio
    
    Args:
        ratio (str): Allocation ratio (e.g., '1:1', '1:4', '1:8')
        formatted_data (list): Formatted data
        
    Returns:
        tuple: (total_usage, total_usage_memory)
    """
    total_usage = 0
    total_usage_memory = 0

    # Loop through the formatted data
    for item in formatted_data:
        vcpus_ratio = item['vCPUs Ratio']
        
        # Check if the host/compute has the matching ratio
        if vcpus_ratio == ratio:
            vcpus_usage = item['VCPUs']['Used']
            total_usage += vcpus_usage

            memory_usage = item['Memory']['Used']
            total_usage_memory += memory_usage

    return total_usage, total_usage_memory

def calculate_total_available_allocation_ratio(ratio, formatted_data):
    """
    Calculate total available resources for a specific allocation ratio
    
    Args:
        ratio (str): Allocation ratio (e.g., '1:1', '1:4', '1:8')
        formatted_data (list): Formatted data
        
    Returns:
        tuple: (total_available, total_available_memory)
    """
    total_capacity, total_capacity_memory = calculate_total_capacity_allocation_ratio(ratio, formatted_data)
    total_usage, total_usage_memory = calculate_total_usage_allocation_ratio(ratio, formatted_data)
    total_available = total_capacity - total_usage
    total_available_memory = total_capacity_memory - total_usage_memory

    return total_available, total_available_memory

def calculate_total_reserved_allocation_ratio(ratio, formatted_data, reserved_data=None):
    """
    Calculate total reserved resources for a specific allocation ratio
    
    Args:
        ratio (str): Allocation ratio (e.g., '1:1', '1:4', '1:8')
        formatted_data (list): Formatted data
        reserved_data (dict): Reserved data
        
    Returns:
        tuple: (total_reserved, total_reserved_memory)
    """
    if reserved_data is None:
        reserved_data = read_reserved_data()
        
    total_reserved = 0
    total_reserved_memory = 0

    for item in formatted_data:
        vcpus_ratio = item['vCPUs Ratio']
        compute_name = item['Compute Name']

        if vcpus_ratio == ratio:
            # Check if the host/compute has reserved resources
            if compute_name in reserved_data:
                reserved_item = reserved_data[compute_name]
                if reserved_item.get('CPU'):
                    total_reserved += int(reserved_item['CPU'])
                if reserved_item.get('RAM'):
                    total_reserved_memory += int(reserved_item['RAM']) * 1024  # Convert from GB to MB

    return total_reserved, total_reserved_memory

def calculate_total_maintenance_allocation_ratio(ratio, formatted_data, reserved_data=None):
    """
    Calculate total maintenance resources for a specific allocation ratio
    
    Args:
        ratio (str): Allocation ratio (e.g., '1:1', '1:4', '1:8')
        formatted_data (list): Formatted data
        reserved_data (dict): Reserved data
        
    Returns:
        tuple: (total_maintenance, total_maintenance_memory)
    """
    if reserved_data is None:
        reserved_data = read_reserved_data()
        
    total_maintenance = 0
    total_maintenance_memory = 0

    for item in formatted_data:
        vcpus_ratio = item['vCPUs Ratio']
        compute_name = item['Compute Name']

        if vcpus_ratio == ratio:
            # Check if the host/compute is marked for maintenance
            if compute_name in reserved_data:
                reserved_item = reserved_data[compute_name]
                kebutuhan = reserved_item.get('Kebutuhan', '')

                # Check if there's a "Backup for maintenance" requirement (case insensitive)
                if "backup for maintenance" in kebutuhan.lower():
                    vcpus_capacity = item['VCPUs']['Capacity']
                    vcpus_used = item['VCPUs']['Used']
                    available_vcpus = vcpus_capacity - vcpus_used
                    total_maintenance += available_vcpus

                    memory_capacity = item['Memory']['Capacity']
                    memory_used = item['Memory']['Used']
                    available_memory = memory_capacity - memory_used
                    total_maintenance_memory += available_memory

    return total_maintenance, total_maintenance_memory

def clean_instance_data(data_list):
    """
    Clean instance data
    
    Args:
        data_list (list): List of instance data
        
    Returns:
        list: Cleaned instance data
    """
    for instance in data_list:
        for key, value in instance.items():
            if pd.isna(value) or value == '':
                instance[key] = '-'
    return data_list

def clean_volume_data(volumes_data):
    """
    Clean volume data
    
    Args:
        volumes_data (list): List of volume data
        
    Returns:
        list: Cleaned volume data
    """
    for volume in volumes_data:
        for key, value in volume.items():
            if isinstance(value, (list, dict)):
                # Handle cases where the value is a list or dictionary
                if not value:
                    volume[key] = '-'
            elif pd.isna(value) or value == '':
                volume[key] = '-'
    return volumes_data
