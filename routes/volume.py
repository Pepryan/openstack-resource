from flask import render_template
from flask_login import login_required
import json
import config
from utils import get_file_last_updated, clean_volume_data
from routes import volume_bp

@volume_bp.route('/volumes', methods=['GET'])
@login_required
def list_all_volumes():
    """
    List all volumes

    Returns:
        Response: Rendered template with volumes
    """
    volumes_last_updated = get_file_last_updated(config.VOLUMES_FILE_PATH)

    # Load volumes data
    with open(config.VOLUMES_FILE_PATH, 'r') as json_file:
        volumes_data = json.load(json_file)

    # Calculate detailed volume statistics
    total_size = sum(vol["Size"] for vol in volumes_data)

    # Get project distribution
    projects = {}
    for vol in volumes_data:
        project = vol.get("Project", "Unknown")
        if project not in projects:
            projects[project] = 0
        projects[project] += 1

    stats = {
        # Project Statistics
        "projects": projects,
        # Volume Size Statistics
        "current_volume_tb": round(total_size / 1024, 2),
        "average_volume_size": round(total_size / len(volumes_data), 2),

        # Volume Count Statistics
        "total_volumes": len(volumes_data),

        # Status Statistics
        "volumes_in_use": len([vol for vol in volumes_data if vol["Status"] == "in-use"]),
        "volumes_available": len([vol for vol in volumes_data if vol["Status"] == "available"]),
        "volumes_creating": len([vol for vol in volumes_data if vol["Status"] == "creating"]),
        "volumes_error": len([vol for vol in volumes_data if vol["Status"] == "error"]),
        "volumes_reserved": len([vol for vol in volumes_data if vol["Status"] == "reserved"]),
        "volumes_attaching": len([vol for vol in volumes_data if vol["Status"] == "attaching"]),
        "volumes_detaching": len([vol for vol in volumes_data if vol["Status"] == "detaching"]),
        "volumes_maintenance": len([vol for vol in volumes_data if vol["Status"] == "maintenance"]),

        # Attachment Statistics
        "attached_volumes": len([vol for vol in volumes_data if vol["Attached to"]]),
        "unattached_volumes": len([vol for vol in volumes_data if not vol["Attached to"]]),

        # Size Distribution
        "volumes_under_100gb": len([vol for vol in volumes_data if vol["Size"] <= 100]),
        "volumes_100gb_to_500gb": len([vol for vol in volumes_data if 100 < vol["Size"] <= 500]),
        "volumes_500gb_to_1tb": len([vol for vol in volumes_data if 500 < vol["Size"] <= 1000]),
        "volumes_over_1tb": len([vol for vol in volumes_data if vol["Size"] > 1000]),

        # Ceph Configuration
        "ceph_erasure_code": config.CEPH_ERASURE_CODE,
        "ceph_total_size_tb": config.CEPH_TOTAL_SIZE_TB,
        "last_updated": volumes_last_updated
    }

    # Calculate usage percentages
    stats.update({
        "current_usage_percentage": round(
            ((stats["current_volume_tb"] * stats["ceph_erasure_code"]) /
             stats["ceph_total_size_tb"]) * 100,
            2
        ),
        "in_use_percentage": round((stats["volumes_in_use"] / stats["total_volumes"]) * 100, 2),
        "available_percentage": round((stats["volumes_available"] / stats["total_volumes"]) * 100, 2),
        "attached_percentage": round((stats["attached_volumes"] / stats["total_volumes"]) * 100, 2)
    })

    # Clean up volume data
    volumes_data = clean_volume_data(volumes_data)

    return render_template('volumes.html',
                         data_list=volumes_data,
                         stats=stats,
                         aio_last_updated=volumes_last_updated)
