from flask import render_template, request, jsonify
from flask_login import login_required
import os
import json
import datetime
import config
from utils import (
    extract_cephdf_data, read_reserved_data, 
    calculate_total_capacity_allocation_ratio,
    calculate_total_usage_allocation_ratio,
    calculate_total_available_allocation_ratio,
    calculate_total_reserved_allocation_ratio,
    calculate_total_maintenance_allocation_ratio,
    get_file_last_updated
)
from models import DataHost
from routes import allocation_bp

@allocation_bp.route('/allocation')
@login_required
def allocation():
    """
    Show allocation information
    
    Returns:
        Response: Rendered template with allocation information
    """
    with open(config.ALLOCATION_FILE_PATH, 'r') as allocation_file:
        allocation_data = allocation_file.readlines()

    with open(config.RATIO_FILE_PATH, 'r') as ratio_file:
        ratio_data = ratio_file.readlines()

    # Call the function to extract data
    cephdf_data = extract_cephdf_data()

    # Load placement check data
    placement_issues = []
    placement_last_check = None
    try:
        with open(config.PLACEMENT_DIFF_FILE_PATH, 'r') as f:
            placement_issues = json.load(f)
            # Get file's last modification time
            placement_last_check = get_file_last_updated(config.PLACEMENT_DIFF_FILE_PATH)
    except (FileNotFoundError, json.JSONDecodeError):
        placement_issues = []
        placement_last_check = datetime.datetime.now().strftime(config.DATE_FORMAT)

    # Load instance IDs check data
    instance_ids_data = []
    instance_ids_last_check = None
    try:
        with open(config.INSTANCE_IDS_CHECK_FILE_PATH, 'r') as f:
            instance_ids_data = json.load(f)
            # Get file's last modification time
            instance_ids_last_check = get_file_last_updated(config.INSTANCE_IDS_CHECK_FILE_PATH)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Access the extracted values
    total_capacity_disk = cephdf_data["Total"]
    raw_used_disk = cephdf_data["Raw Used"]
    raw_used_percentage_disk = cephdf_data["%Raw Used"]

    # Convert total capacity from PiB to TB
    total_capacity_disk_tb = float(total_capacity_disk.split()[0]) * 1024
    raw_used_disk_tb = round(float(raw_used_disk.split()[0]) * 1024, 2)
    avail_disk_tb = round(float(total_capacity_disk_tb - raw_used_disk_tb), 2)
    avail_percentage_disk = round(float(100 - float(raw_used_percentage_disk)), 2)

    first_line = ratio_data[0].strip()
    site_name = first_line.split('-')[0].upper()

    allocation_last_updated = get_file_last_updated(config.ALLOCATION_FILE_PATH)

    formatted_data = []

    for allocation_line, ratio_line in zip(allocation_data, ratio_data):
        allocation_parts = allocation_line.strip().split()
        ratio_parts = ratio_line.strip().split()
        if len(allocation_parts) >= 6 and len(ratio_parts) >= 3:
            compute_name = allocation_parts[1]
            vcpus_used = int(allocation_parts[5])
            vcpus_ratio = DataHost.get_vcpus_ratio(compute_name)
            core = config.CORE_COMPUTE
            vcpus_capacity = int(vcpus_ratio * config.CORE_COMPUTE)
            vcpus_usage_percentage = round((vcpus_used / vcpus_capacity) * 100, 2)

            memory_used = int(allocation_parts[7])
            memory_ratio = float(ratio_parts[2]) 

            memory_capacity = int(allocation_parts[8]) * memory_ratio
            memory_usage_percentage = round((memory_used / memory_capacity) * 100, 2)

            reserved_data = read_reserved_data()

            reserved_item = reserved_data.get(compute_name, {
                'CPU': '',
                'RAM': '',
                'Kebutuhan': ''
            })

            # Calculate Availability After Reservation for CPU
            if reserved_item['CPU']:
                cpu_availability_after_reservation = vcpus_capacity - vcpus_used - int(reserved_item['CPU'])
            else:
                cpu_availability_after_reservation = vcpus_capacity - vcpus_used

            # Calculate Availability After Reservation for RAM
            try:
                ram_reserved = int(reserved_item['RAM']) * 1024
            except ValueError:
                ram_reserved = 0

            ram_availability_after_reservation = round((memory_capacity - memory_used - ram_reserved) / 1024, 2)

            formatted_data.append({
                'vCPUs Ratio': f"1:{int(vcpus_ratio)}",
                'Compute Name': compute_name,
                'VCPUs': {
                    'Used': vcpus_used,
                    'Core': core,
                    'Capacity': vcpus_capacity,
                    'Available': vcpus_capacity - vcpus_used,
                    'Usage Percentage': vcpus_usage_percentage
                },
                'Memory': {
                    'Used': memory_used,
                    'Capacity': memory_capacity,
                    'Available (GB)': f"{float(memory_capacity - memory_used)/1024:.2f}",
                    'Usage Percentage': memory_usage_percentage
                },
                'Reserved': {
                    'CPU': reserved_item['CPU'],
                    'RAM': reserved_item['RAM'],
                    'Kebutuhan': reserved_item['Kebutuhan']
                },
                'CPU Availability After Reservation': cpu_availability_after_reservation,
                'RAM Availability After Reservation': ram_availability_after_reservation
            })
    
    # Calculate totals for different allocation ratios
    total_capacity_1_1, total_capacity_memory_1_1 = calculate_total_capacity_allocation_ratio('1:1', formatted_data)
    total_capacity_1_4, total_capacity_memory_1_4 = calculate_total_capacity_allocation_ratio('1:4', formatted_data)
    total_capacity_1_8, total_capacity_memory_1_8 = calculate_total_capacity_allocation_ratio('1:8', formatted_data)

    total_usage_1_1, total_usage_memory_1_1 = calculate_total_usage_allocation_ratio('1:1', formatted_data)
    total_usage_1_4, total_usage_memory_1_4 = calculate_total_usage_allocation_ratio('1:4', formatted_data)
    total_usage_1_8, total_usage_memory_1_8 = calculate_total_usage_allocation_ratio('1:8', formatted_data)

    total_available_1_1, total_available_memory_1_1 = calculate_total_available_allocation_ratio('1:1', formatted_data)
    total_available_1_4, total_available_memory_1_4 = calculate_total_available_allocation_ratio('1:4', formatted_data)
    total_available_1_8, total_available_memory_1_8 = calculate_total_available_allocation_ratio('1:8', formatted_data)

    # Calculate percentages
    percentage_total_capacity_1_1 = round((total_capacity_1_1 / total_capacity_1_1) * 100, 2)
    percentage_total_usage_1_1 = round((total_usage_1_1 / total_capacity_1_1) * 100, 2)
    percentage_total_available_1_1 = round((total_available_1_1 / total_capacity_1_1) * 100, 2)

    # Calculate shared totals
    total_usage_shared = total_usage_1_4 + total_usage_1_8
    total_available_shared = total_available_1_4 + total_available_1_8
    total_capacity_shared = total_capacity_1_4 + total_capacity_1_8
    percentage_total_capacity_shared = 100
    percentage_total_usage_shared = round((total_usage_shared / total_capacity_shared) * 100, 2)
    percentage_total_available_shared = round((total_available_shared / total_capacity_shared) * 100, 2)

    # Calculate reserved totals
    reserved_data = read_reserved_data()
    
    # Calculate reserved for dedicated (1:1)
    total_reserved_1_1, total_reserved_memory_1_1 = calculate_total_reserved_allocation_ratio('1:1', formatted_data, reserved_data)
    percentage_total_reserved_1_1 = round((total_reserved_1_1 / total_capacity_1_1) * 100, 2)

    # Calculate reserved for shared (1:4)
    total_reserved_1_4, total_reserved_memory_1_4 = calculate_total_reserved_allocation_ratio('1:4', formatted_data, reserved_data)

    # Calculate reserved for shared (1:8)
    total_reserved_1_8, total_reserved_memory_1_8 = calculate_total_reserved_allocation_ratio('1:8', formatted_data, reserved_data)

    percentage_total_reserved_shared = round((total_reserved_1_4 + total_reserved_1_8)/total_capacity_shared * 100, 2)

    # Calculate maintenance totals
    # Calculate maintenance for dedicated (1:1)
    total_maintenance_1_1, total_maintenance_memory_1_1 = calculate_total_maintenance_allocation_ratio('1:1', formatted_data, reserved_data)
    percentage_total_maintenance_1_1 = round((total_maintenance_1_1 / total_capacity_1_1) * 100, 2)

    # Calculate maintenance for shared (1:4)
    total_maintenance_1_4, total_maintenance_memory_1_4 = calculate_total_maintenance_allocation_ratio('1:4', formatted_data, reserved_data)

    # Calculate maintenance for shared (1:8)
    total_maintenance_1_8, total_maintenance_memory_1_8 = calculate_total_maintenance_allocation_ratio('1:8', formatted_data, reserved_data)
    percentage_total_maintenance_shared = round((total_maintenance_1_4 + total_maintenance_1_8) / total_capacity_shared * 100, 2)

    # Calculate final available totals
    total_available_final_1_1 = total_available_1_1 - total_reserved_1_1 - total_maintenance_1_1
    total_available_final_1_4 = total_available_1_4 - total_reserved_1_4 - total_maintenance_1_4
    total_available_final_1_8 = total_available_1_8 - total_reserved_1_8 - total_maintenance_1_8
    percentage_total_available_final_1_1 = round((total_available_final_1_1 / total_capacity_1_1)*100, 2)
    percentage_total_available_final_shared = round((total_available_final_1_4 + total_available_final_1_8) / total_capacity_shared * 100, 2)

    # Calculate memory totals
    total_capacity_memory_all = round((total_capacity_memory_1_1 + total_capacity_memory_1_4 + total_capacity_memory_1_8) / 1048576, 2)
    total_usage_memory_all = round((total_usage_memory_1_1 + total_usage_memory_1_4 + total_usage_memory_1_8) / 1048576, 2)
    total_available_memory_all = round((total_available_memory_1_1 + total_available_memory_1_4 + total_available_memory_1_8) / 1048576, 2)
    total_reserved_memory_all = round((total_reserved_memory_1_1 + total_reserved_memory_1_4 + total_reserved_memory_1_8) / 1048576, 2)
    total_maintenance_memory_all = round((total_maintenance_memory_1_1 + total_maintenance_memory_1_4 + total_maintenance_memory_1_8) / 1048576, 2)

    total_available_memory_final = round(total_available_memory_all - total_reserved_memory_all - total_maintenance_memory_all, 2)

    # Calculate memory percentages
    percentage_total_usage_memory_all = round(total_usage_memory_all / total_capacity_memory_all * 100, 2)
    percentage_total_available_memory_all = round(total_available_memory_all / total_capacity_memory_all * 100, 2)
    percentage_total_reserved_memory_all = round(total_reserved_memory_all / total_capacity_memory_all * 100, 2)
    percentage_total_maintenance_memory_all = round(total_maintenance_memory_all / total_capacity_memory_all * 100, 2)
    percentage_total_available_memory_final_all = round(total_available_memory_final / total_capacity_memory_all * 100, 2)

    return render_template('allocation.html', 
                          data=formatted_data, 
                          site_name=site_name,
                          allocation_last_updated=allocation_last_updated, 
    
                          total_capacity_1_1=total_capacity_1_1, 
                          total_usage_1_1=total_usage_1_1, 
                          total_available_raw_1_1=total_available_1_1,

                          percentage_total_capacity_1_1=percentage_total_capacity_1_1,
                          percentage_total_usage_1_1=percentage_total_usage_1_1,
                          percentage_total_available_1_1=percentage_total_available_1_1,
                          
                          total_capacity_1_4=total_capacity_1_4, 
                          total_usage_1_4=total_usage_1_4, 
                          total_available_raw_1_4=total_available_1_4,

                          total_capacity_1_8=total_capacity_1_8, 
                          total_usage_1_8=total_usage_1_8, 
                          total_available_raw_1_8=total_available_1_8,

                          percentage_total_capacity_shared=percentage_total_capacity_shared,
                          percentage_total_usage_shared=percentage_total_usage_shared,
                          percentage_total_available_shared=percentage_total_available_shared,
                          percentage_total_reserved_1_1=percentage_total_reserved_1_1,
                          percentage_total_maintenance_1_1=percentage_total_maintenance_1_1,
                          percentage_total_available_final_1_1=percentage_total_available_final_1_1,
                          percentage_total_reserved_shared=percentage_total_reserved_shared,
                          percentage_total_maintenance_shared=percentage_total_maintenance_shared,
                          percentage_total_available_final_shared=percentage_total_available_final_shared,

                          total_reserved_1_1=total_reserved_1_1,
                          total_reserved_1_4=total_reserved_1_4,
                          total_reserved_1_8=total_reserved_1_8,

                          total_maintenance_1_1=total_maintenance_1_1,
                          total_maintenance_1_4=total_maintenance_1_4,
                          total_maintenance_1_8=total_maintenance_1_8,

                          total_available_final_1_1=total_available_final_1_1,
                          total_available_final_1_4=total_available_final_1_4,
                          total_available_final_1_8=total_available_final_1_8,

                          total_capacity_memory_all=total_capacity_memory_all,
                          total_usage_memory_all=total_usage_memory_all,
                          total_available_memory_all=total_available_memory_all,

                          total_reserved_memory_all=total_reserved_memory_all,
                          total_maintenance_memory_all=total_maintenance_memory_all,
                          total_available_memory_final=total_available_memory_final,

                          percentage_total_usage_memory_all=percentage_total_usage_memory_all,
                          percentage_total_available_memory_all=percentage_total_available_memory_all,
                          percentage_total_reserved_memory_all=percentage_total_reserved_memory_all,
                          percentage_total_maintenance_memory_all=percentage_total_maintenance_memory_all,
                          percentage_total_available_memory_final_all=percentage_total_available_memory_final_all,

                          total_capacity_disk_tb=total_capacity_disk_tb,
                          raw_used_disk_tb=raw_used_disk_tb,
                          raw_used_percentage_disk=raw_used_percentage_disk,
                          avail_disk_tb=avail_disk_tb,
                          avail_percentage_disk=avail_percentage_disk,

                          placement_issues=placement_issues,
                          placement_last_check=placement_last_check,
                          instance_ids_data=instance_ids_data,
                          instance_ids_last_check=instance_ids_last_check
                         )

@allocation_bp.route('/save_reserved', methods=['POST'])
@login_required
def save_reserved():
    """
    Save reserved data
    
    Returns:
        Response: JSON response with success status
    """
    try:
        data = request.get_json()

        # Ensure data has the correct format
        if not isinstance(data, dict):
            raise ValueError("Data tidak valid.")

        reserved_data = read_reserved_data()

        for compute_name, compute_data in data.items():
            cpu = compute_data.get('CPU', '') 
            ram = compute_data.get('RAM', '')
            kebutuhan = compute_data.get('Kebutuhan', '')

            # If the compute doesn't exist in reserved data, add it with empty values
            if compute_name not in reserved_data:
                reserved_data[compute_name] = {"CPU": "", "RAM": "", "Kebutuhan": ""}

            # Update or add data for the compute
            reserved_data[compute_name]["CPU"] = cpu
            reserved_data[compute_name]["RAM"] = ram
            reserved_data[compute_name]["Kebutuhan"] = kebutuhan

        # Save data to JSON file
        with open(config.RESERVED_FILE_PATH, 'w') as f:
            json.dump(reserved_data, f, indent=4)

        return jsonify({"success": True}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
