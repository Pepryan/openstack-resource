from flask import render_template, request, jsonify
from flask_login import login_required
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import csv
import numpy as np
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

@instance_bp.route('/get_allocation_data', methods=['GET'])
@login_required
def get_allocation_data():
    """
    Get allocation data for interactive Chart.js visualization

    Returns:
        Response: JSON response with allocation data grouped by project and host
    """
    print("Starting get_allocation_data function")
    try:
        # Load instance data
        data = pd.read_csv(config.AIO_CSV_PATH, delimiter=config.CSV_DELIMITER)

        # Load volume data
        with open(config.VOLUMES_FILE_PATH, 'r') as volumes_file:
            volumes_data = json.load(volumes_file)
    except Exception as e:
        print(f"Error loading data: {e}")
        return jsonify({"error": f"Error loading data: {e}"}), 500

    # Create a dictionary to store volume information by server_id
    volume_info_by_server = {}
    for volume in volumes_data:
        attachments = volume.get("Attached to", [])
        if attachments:
            server_id = attachments[0]["server_id"]
            device = attachments[0]["device"]
            volume_name = volume["Name"] if volume["Name"] else volume["ID"]
            volume_size = volume.get("Size", 0)
            if server_id not in volume_info_by_server:
                volume_info_by_server[server_id] = []
            volume_info_by_server[server_id].append({"device": device, "name": volume_name, "size": volume_size})

    # Get host information
    hosts = {}
    with open(config.RATIO_FILE_PATH, 'r') as ratio_file:
        for line in ratio_file:
            parts = line.strip().split(',')
            if len(parts) == 3:
                host_name = parts[0].strip()
                ratio_value = float(parts[1])
                tier = "1:1" if ratio_value == 1 else "1:4" if ratio_value == 4 else "1:8" if ratio_value == 8 else "Unknown"
                vcpus_total = ratio_value * config.CORE_COMPUTE
                hosts[host_name] = {
                    "name": host_name,
                    "tier": tier,
                    "ratio": ratio_value,
                    "vcpus_total": vcpus_total,
                    "vcpus_used": 0,
                    "instances": []
                }

    # Group instances by project and host
    projects = {}

    for _, row in data.iterrows():
        instance_id = row["ID"]
        instance_name = row["Name"]
        instance_host = row["Host"]
        instance_project = row["Project"]
        instance_status = row["Status"]

        # Convert CPU to integer
        try:
            instance_vcpus = int(row["CPU"])
        except (ValueError, TypeError):
            instance_vcpus = 0
            print(f"Warning: Could not convert CPU value '{row['CPU']}' to integer for instance {instance_name}")

        # Convert RAM to integer (handle values like "1G")
        try:
            ram_value = row["RAM"]
            if isinstance(ram_value, str):
                if ram_value.endswith('G'):
                    # Convert GB to MB (1G = 1024 MB)
                    instance_ram = int(float(ram_value.rstrip('G')) * 1024)
                elif ram_value.endswith('M'):
                    instance_ram = int(float(ram_value.rstrip('M')))
                else:
                    # Try direct conversion
                    instance_ram = int(ram_value)
            else:
                instance_ram = int(ram_value)
        except (ValueError, TypeError):
            instance_ram = 0
            print(f"Warning: Could not convert RAM value '{row['RAM']}' for instance {instance_name}")

        # Skip if host not found
        if instance_host not in hosts:
            continue

        # Calculate total disk size
        total_disk_size = 0
        volumes = []
        if instance_id in volume_info_by_server:
            for vol in volume_info_by_server[instance_id]:
                size = vol.get("size", 0)
                if isinstance(size, (int, float)):
                    total_disk_size += size
                volumes.append({
                    "name": vol["name"],
                    "size": vol["size"],
                    "device": vol["device"]
                })

        # Create instance object
        instance = {
            "id": instance_id,
            "name": instance_name,
            "host": instance_host,
            "status": instance_status,
            "vcpus": instance_vcpus,
            "ram": instance_ram,
            "ram_gb": round(instance_ram / 1024, 2),
            "volumes": volumes,
            "total_disk": total_disk_size,
            "tier": hosts[instance_host]["tier"]
        }

        # Add to project
        if instance_project not in projects:
            projects[instance_project] = {
                "name": instance_project,
                "instances": [],
                "vcpus_total": 0,
                "ram_total": 0,
                "disk_total": 0
            }

        projects[instance_project]["instances"].append(instance)
        projects[instance_project]["vcpus_total"] += instance_vcpus
        projects[instance_project]["ram_total"] += instance_ram
        projects[instance_project]["disk_total"] += total_disk_size

        # Update host information
        hosts[instance_host]["vcpus_used"] += instance_vcpus
        hosts[instance_host]["instances"].append(instance)

    # Convert to lists for JSON response
    projects_list = list(projects.values())
    hosts_list = list(hosts.values())

    # Sort projects by name
    projects_list.sort(key=lambda x: x["name"])

    # Sort hosts by name
    hosts_list.sort(key=lambda x: x["name"])

    # Calculate total resources
    total_vcpus_used = sum(host["vcpus_used"] for host in hosts_list)
    total_vcpus_capacity = sum(host["vcpus_total"] for host in hosts_list)

    try:
        response = {
            "projects": projects_list,
            "hosts": hosts_list,
            "totals": {
                "vcpus_used": total_vcpus_used,
                "vcpus_capacity": total_vcpus_capacity,
                "vcpus_free": total_vcpus_capacity - total_vcpus_used,
                "projects_count": len(projects_list),
                "hosts_count": len(hosts_list),
                "instances_count": sum(len(project["instances"]) for project in projects_list)
            },
            "last_updated": get_file_last_updated(config.AIO_CSV_PATH)
        }

        # Test that the response can be serialized to JSON
        json_response = jsonify(response)
        return json_response
    except Exception as e:
        print(f"Error creating JSON response: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@instance_bp.route('/generate_improved_vcpu_plot', methods=['GET'])
@login_required
def generate_improved_vcpu_plot():
    """
    Generate an improved vCPU allocation plot with better visualization

    Returns:
        Response: JSON response with image path
    """
    destination_host = request.args.get('host')
    if not destination_host:
        return jsonify({"error": "Host parameter is required"}), 400

    # Load instance data
    data = pd.read_csv(config.AIO_CSV_PATH, delimiter=config.CSV_DELIMITER)

    # Filter instances for the selected host
    host_instances = data[data['Host'] == destination_host]

    if host_instances.empty:
        return jsonify({"error": f"No instances found for host {destination_host}"}), 404

    # Get host ratio information
    host_ratio = 1
    with open(config.RATIO_FILE_PATH, 'r') as ratio_file:
        for line in ratio_file:
            parts = line.strip().split(',')
            if len(parts) == 3 and parts[0].strip() == destination_host:
                host_ratio = float(parts[1])
                break

    # Calculate host capacity
    host_capacity = config.CORE_COMPUTE * host_ratio

    # Group instances by project
    projects = {}
    for _, instance in host_instances.iterrows():
        project = instance['Project']
        if project not in projects:
            projects[project] = []

        # Add instance to project
        projects[project].append({
            'name': instance['Name'],
            'vcpus': int(instance['CPU']),
            'status': instance['Status']
        })

    # Set up the plot with improved styling
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 8))

    # Use a better color palette
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(projects)))

    # Set background color
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')

    # Setup grid
    ax.grid(color='#333344', linestyle='-', linewidth=0.5, alpha=0.7)

    # Calculate layout
    square_size = 1
    margin = 0.5
    max_cols = 16

    # Track position
    x, y = margin, margin
    max_x = 0

    # Track legend entries
    legend_handles = []
    legend_labels = []

    # Draw instances grouped by project
    for i, (project_name, instances) in enumerate(projects.items()):
        project_color = colors[i]

        # Sort instances by status (ACTIVE first) and then by name
        instances.sort(key=lambda inst: (0 if inst['status'] == 'ACTIVE' else 1, inst['name']))

        for instance in instances:
            # Determine instance color based on status
            instance_color = project_color
            if instance['status'] != 'ACTIVE':
                # Use a lighter version of the project color for non-active instances
                instance_color = tuple(list(project_color[:3]) + [0.5])

            # Draw rectangle for each vCPU
            for _ in range(instance['vcpus']):
                rect = plt.Rectangle((x, y), square_size, square_size,
                                    facecolor=instance_color, edgecolor='white',
                                    linewidth=0.5, alpha=0.8)
                ax.add_patch(rect)

                # Move to next position
                x += square_size
                if x >= margin + max_cols * square_size:
                    x = margin
                    y += square_size

            # Update max_x
            max_x = max(max_x, x)

        # Add project to legend
        project_rect = plt.Rectangle((0, 0), 1, 1, facecolor=project_color, edgecolor='white', linewidth=0.5)
        legend_handles.append(project_rect)
        legend_labels.append(f"{project_name} ({sum(inst['vcpus'] for inst in instances)} vCPUs)")

    # Draw remaining capacity
    total_used = sum(sum(inst['vcpus'] for inst in instances) for instances in projects.values())
    remaining = int(host_capacity - total_used)

    if remaining > 0:
        # Use gray for remaining capacity
        remaining_color = (0.3, 0.3, 0.3, 0.5)

        for _ in range(remaining):
            rect = plt.Rectangle((x, y), square_size, square_size,
                                facecolor=remaining_color, edgecolor='white',
                                linewidth=0.5, alpha=0.5)
            ax.add_patch(rect)

            # Move to next position
            x += square_size
            if x >= margin + max_cols * square_size:
                x = margin
                y += square_size

            # Update max_x
            max_x = max(max_x, x)

        # Add remaining to legend
        remaining_rect = plt.Rectangle((0, 0), 1, 1, facecolor=remaining_color, edgecolor='white', linewidth=0.5)
        legend_handles.append(remaining_rect)
        legend_labels.append(f"Available ({remaining} vCPUs)")

    # Set axis limits
    max_y = y + square_size if x > margin else y
    ax.set_xlim(0, margin + max_cols * square_size + margin)
    ax.set_ylim(0, max_y + margin)

    # Remove axis ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Add title and labels
    plt.title(f"vCPU Allocation for {destination_host} (Capacity: {int(host_capacity)} vCPUs)",
              fontsize=16, color='white', pad=20)

    # Add legend with better positioning and styling
    legend = ax.legend(handles=legend_handles, labels=legend_labels,
                      loc='upper center', bbox_to_anchor=(0.5, -0.05),
                      fancybox=True, shadow=True, ncol=3, fontsize=10)
    legend.get_frame().set_facecolor('#2a2a3e')
    legend.get_frame().set_edgecolor('#4a4a5e')

    # Add usage summary
    usage_percent = (total_used / host_capacity) * 100 if host_capacity > 0 else 0
    usage_text = f"Usage: {total_used}/{int(host_capacity)} vCPUs ({usage_percent:.1f}%)"
    ax.text(0.5, 0.02, usage_text, transform=fig.transFigure,
            ha='center', va='bottom', fontsize=12, color='white')

    # Save the figure
    os.makedirs('static/results', exist_ok=True)
    image_path = f'static/results/{destination_host}_improved.png'
    plt.savefig(image_path, bbox_inches='tight', dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)

    return jsonify({
        'image_path': image_path,
        'host': destination_host,
        'capacity': int(host_capacity),
        'used': total_used,
        'available': remaining,
        'usage_percent': usage_percent
    })

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
        total_disk_size = 0

        # Get compute tier information based on host
        host = instance["Host"]
        tier = "Unknown"
        with open(config.RATIO_FILE_PATH, 'r') as ratio_file:
            for line in ratio_file:
                parts = line.strip().split(',')
                if len(parts) == 3 and parts[0].strip() == host:
                    ratio_value = float(parts[1])
                    if ratio_value == 1:
                        tier = "1:1"
                    elif ratio_value == 4:
                        tier = "1:4"
                    elif ratio_value == 8:
                        tier = "1:8"
                    break

        instance["Tier"] = tier

        if server_id in volume_info_by_server:
            volumes = volume_info_by_server[server_id]
            volumes.sort(key=lambda vol: vol["device"])

            # Create a clean format for CSV/Excel export
            csv_volume_info = []
            for vol in volumes:
                device = vol["device"].replace("/dev/", "")  # Remove /dev/ prefix for cleaner display
                # Format for better Excel readability - use semicolons for volume separation and commas for properties
                csv_volume_info.append(f"{device}, {vol['name']}, {vol['size']}GB")

            # Store the CSV-friendly format in a separate field for export
            # Use semicolons to separate volumes, which works better in Excel
            instance["Volumes_CSV"] = "; ".join(csv_volume_info)

            # Create HTML format for display with better structure
            html_volume_info = []
            for vol in volumes:
                device = vol["device"].replace("/dev/", "")  # Remove /dev/ prefix for cleaner display

                # Format the volume name to handle long names better
                vol_name = vol['name']
                vol_size = vol['size']

                # Create a structured HTML layout for each volume
                html_volume_info.append(
                    f"<div class='volume-item'>"
                    f"<span class='volume-device'>{device}</span>"
                    f"<span class='volume-name'>{vol_name}</span>"
                    f"<span class='volume-size'>{vol_size} GB</span>"
                    f"</div>"
                )

            # Join with no breaks for a more compact display
            instance["Volumes"] = "".join(html_volume_info)

            # Calculate total disk size
            for vol in volumes:
                size = vol.get("size", 0)
                if isinstance(size, (int, float)):
                    total_disk_size += size
        else:
            instance["Volumes"] = '-'
            instance["Volumes_CSV"] = '-'

        # Convert total disk size to GB with 2 decimal places
        if total_disk_size > 0:
            instance["Total Disk"] = f"{total_disk_size} GB"
        else:
            instance["Total Disk"] = "-"

    # Clean up instance data
    data_list = clean_instance_data(data_list)

    return render_template('list_all_instances.html',
                           data_list=data_list,
                           aio_last_updated=aio_last_updated)
