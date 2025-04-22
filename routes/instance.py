from flask import render_template, request, jsonify
from flask_login import login_required
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import csv
from models import DataHost
import config
from utils import get_file_last_updated, clean_instance_data
from routes import instance_bp

@instance_bp.route('/get_instances', methods=['GET'])
@login_required
def get_instances():
    """
    Get instances on a specific compute host or a specific instance
    
    Returns:
        Response: JSON response with instances
    """
    # Load data
    data = pd.read_csv(config.AIO_CSV_PATH, delimiter=config.CSV_DELIMITER)
    
    host = request.args.get('host')
    instance_id = request.args.get('id')

    if instance_id:
        # Filter by instance ID
        instance = data[data['ID'] == instance_id][['Name', 'CPU', 'Host']]
        instance_json = instance.to_dict(orient='records')
        return jsonify({'instances': instance_json})

    # If no instance ID is provided, return all instances for the host
    instances = data[data['Host'] == host][['Name', 'CPU', 'Host']]
    instances_json = instances.to_dict(orient='records')
    return jsonify({'instances': instances_json})

@instance_bp.route('/get_destination_host_instances', methods=['GET'])
@login_required
def get_destination_host_instances():
    """
    Get instances on a specific destination compute host
    
    Returns:
        Response: JSON response with instances and vCPU information
    """
    # Load data
    data = pd.read_csv(config.AIO_CSV_PATH, delimiter=config.CSV_DELIMITER)
    
    host = request.args.get('host')
    instances = data[data['Host'] == host][['Name', 'CPU']]
    instances_json = instances.to_dict(orient='records')
    
    vcpus_used = DataHost.get_vcpus_used(host)
    vcpus_ratio = DataHost.get_vcpus_ratio(host)    
    vcpus_total = vcpus_ratio * config.CORE_COMPUTE
    vcpus_free = vcpus_total - vcpus_used
    
    return jsonify({
        'instances': instances_json,
        'vcpus_total': vcpus_total,
        'vcpus_free': vcpus_free,
        'vcpus_used': vcpus_used,
    })

@instance_bp.route('/get_instance_vcpus_used', methods=['GET'])
@login_required
def get_instance_vcpus_used():
    """
    Get vCPUs used by a specific instance
    
    Returns:
        Response: JSON response with vCPUs used
    """
    # Load data
    data = pd.read_csv(config.AIO_CSV_PATH, delimiter=config.CSV_DELIMITER)
    
    instance_name = request.args.get('name')
    instance_host = data[data['Name'] == instance_name]['Host'].values[0]
    vcpus_used_instance = int(data[data['Name'] == instance_name]['CPU'].values[0])
    
    return jsonify(vcpus_used_instance)

@instance_bp.route('/generate_vcpu_allocation_plot', methods=['GET'])
@login_required
def generate_vcpu_allocation_plot():
    """
    Generate a vCPU allocation plot for a specific destination host
    
    Returns:
        Response: JSON response with image path
    """
    destination_host = request.args.get('destination_host')
    file_path = config.AIO_CSV_PATH
    longest_string = ""
    vcpu_claimed = []
    vcpu_labels = []
    
    with open(file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')  
        next(csvreader)  
        for row in csvreader:
            if destination_host == row[10]:  
                if row[3] == 'ACTIVE' or row[3] == 'SHUTOFF':  
                    vcpu_labels.append(f"{row[3][0]}_{row[0]}__{row[2]}")  
                    vcpu_claimed.append(int(row[11]))  
                    if len(f"{row[0]}__{row[2]}") > len(longest_string):
                        longest_string = f"{row[0]}__{row[2]}"
    
    with open(config.RATIO_FILE_PATH, 'r') as ratio_file:
        for line in ratio_file:
            parts = line.strip().split(',')
            if len(parts) == 3 and parts[0] == destination_host:
                ratio_value = float(parts[1])
                host_size = config.CORE_COMPUTE
                host_size = host_size * ratio_value
                break  
    
    total_vcpus = sum(vcpu_claimed)
    num_cols = 16
    small_square_size = host_size / num_cols
    num_rows = (total_vcpus + num_cols - 1) // num_cols
    
    colors = plt.cm.get_cmap('tab20', len(vcpu_claimed))
    
    fig, ax = plt.subplots()
    
    x_pos = 0
    y_pos = 0
    legend_handles = []
    unique_labels = set(vcpu_labels)
    
    for i, (vcpu, label) in enumerate(zip(vcpu_claimed, vcpu_labels)):
        color = colors(i)
        for _ in range(vcpu):
            rect = plt.Rectangle((x_pos, y_pos), small_square_size, small_square_size, color=color, alpha=0.7)
            ax.add_patch(rect)   
            ax.text(x_pos + small_square_size / 2, y_pos + small_square_size / 2, str(vcpu),
                    color='white', ha='center', va='center')
            x_pos += small_square_size
            if x_pos >= host_size:
                x_pos = 0
                y_pos += small_square_size
        if label in unique_labels:
            legend_handles.append(rect)
            unique_labels.remove(label)
    
    remaining_squares = int(host_size - total_vcpus)  
    for _ in range(remaining_squares):
        rect = plt.Rectangle((x_pos, y_pos), small_square_size, small_square_size, color='gray', alpha=0.7)
        ax.add_patch(rect)
        x_pos += small_square_size
        if x_pos >= host_size:
            x_pos = 0
            y_pos += small_square_size

    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(0, host_size)
    ax.set_ylim(0, host_size)

    ax.set_xticks([i * small_square_size for i in range(num_cols + 1)])
    ax.set_yticks([i * small_square_size for i in range(num_rows + 1)])
    ax.set_xticklabels([str(i) for i in range(num_cols + 1)])
    ax.set_yticklabels([str(i) for i in range(num_rows + 1)])

    ankor = 1.6 + (len(longest_string) * 0.03)
    if ankor > 3.3:
        ankor = 3.325
    ax.legend(handles=legend_handles, labels=vcpu_labels, loc='upper right', bbox_to_anchor=(ankor, 1))

    image_path = f'static/results/{destination_host}.png'
    plt.title(destination_host)
    plt.savefig(image_path, bbox_inches='tight')
    
    response_data = {
        'image_path': f"static/results/{destination_host}.png",
    }
    return jsonify(response_data)

@instance_bp.route('/list-all-instances', methods=['GET'])
@login_required
def list_all_instances():
    """
    List all instances
    
    Returns:
        Response: Rendered template with instances
    """
    aio_last_updated = get_file_last_updated(config.AIO_CSV_PATH)
    
    data = pd.read_csv(config.AIO_CSV_PATH, delimiter=config.CSV_DELIMITER)
    data_list = data.to_dict(orient='records')

    # Get the instance ID from the query parameters
    instance_id = request.args.get('id')

    if instance_id:
        # Filter the data for the specific instance ID
        data_list = [instance for instance in data_list if instance["ID"] == instance_id]

    # Load the JSON data that contains volume information
    with open(config.VOLUMES_FILE_PATH, 'r') as volumes_file:
        volumes_data = json.load(volumes_file)

    # Create a dictionary to store volume information by server_id
    volume_info_by_server = {}
    for volume in volumes_data:
        attachments = volume.get("Attached to", [])
        if attachments:
            server_id = attachments[0]["server_id"]
            device = attachments[0]["device"]
            volume_name = volume["Name"] if volume["Name"] else volume["ID"]
            volume_size = volume.get("Size", "-")
            if server_id not in volume_info_by_server:
                volume_info_by_server[server_id] = []
            volume_info_by_server[server_id].append({"device": device, "name": volume_name, "size": volume_size})

    # Update the instance data with volume information
    for instance in data_list:
        server_id = instance["ID"]
        if server_id in volume_info_by_server:
            volumes = volume_info_by_server[server_id]
            volumes.sort(key=lambda vol: vol["device"])
            volume_info = [f"{vol['name']} (Size: {vol['size']}, Device: {vol['device']})" for vol in volumes]
            instance["Volumes"] = "<br>".join(volume_info)
        else:
            instance["Volumes"] = '-'

    # Clean up instance data
    data_list = clean_instance_data(data_list)

    return render_template('list_all_instances.html',
                           data_list=data_list,
                           aio_last_updated=aio_last_updated)
