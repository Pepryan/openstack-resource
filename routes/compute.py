from flask import render_template, request, jsonify
from flask_login import login_required
from models import DataHost
import pandas as pd
import config
from utils import get_sorted_computes
from routes import compute_bp

@compute_bp.route('/')
@login_required
def index():
    """
    Render the index page with a list of all compute hosts

    Returns:
        Response: Rendered index page
    """
    hosts = get_sorted_computes()
    return render_template('index.html', source_hosts=hosts)

@compute_bp.route('/get_source_hosts', methods=['GET'])
@login_required
def get_source_hosts():
    """
    Get a list of all compute hosts

    Returns:
        Response: JSON response with list of compute hosts
    """
    hosts = get_sorted_computes()
    return jsonify(hosts)

@compute_bp.route('/get_host_allocation', methods=['GET'])
@login_required
def get_host_allocation():
    """
    Get allocation information for a specific compute host

    Returns:
        Response: JSON response with allocation information
    """
    host = request.args.get('host')

    # Get vCPU information
    vcpus_used = DataHost.get_vcpus_used(host)
    vcpus_ratio = DataHost.get_vcpus_ratio(host)

    core_compute = config.CORE_COMPUTE
    vcpus_total = core_compute * vcpus_ratio
    vcpus_free = vcpus_total - vcpus_used

    # Get RAM information
    ram_used = DataHost.get_ram_used(host)
    ram_total = DataHost.get_ram_total(host)
    ram_free = DataHost.get_ram_free(host)
    ram_ratio = DataHost.get_ram_ratio(host)

    # Format RAM values for display
    ram_used_gb = ram_used / 1024
    ram_total_gb = ram_total / 1024
    ram_free_gb = ram_free / 1024

    response_data = {
        'vcpus_used': vcpus_used,
        'vcpus_total': vcpus_total,
        'vcpus_free': vcpus_free,
        'vcpus_ratio': vcpus_ratio,
        'ram_used': ram_used,
        'ram_total': ram_total,
        'ram_free': ram_free,
        'ram_ratio': ram_ratio,
        'ram_used_gb': round(ram_used_gb, 2),
        'ram_total_gb': round(ram_total_gb, 2),
        'ram_free_gb': round(ram_free_gb, 2)
    }
    return jsonify(response_data)

@compute_bp.route('/get_compute_with_free_vcpus', methods=['GET'])
@login_required
def get_compute_with_free_vcpus():
    """
    Get a list of compute hosts with at least the specified number of free vCPUs

    Returns:
        Response: JSON response with list of compute hosts
    """
    vcpu_required = int(request.args.get('vcpu'))

    # Load data
    data = pd.read_csv(config.AIO_CSV_PATH, delimiter=config.CSV_DELIMITER)

    compute_list = []
    for compute in data['Host']:
        vcpus_total = DataHost.get_vcpus_ratio(compute) * config.CORE_COMPUTE
        vcpus_used = DataHost.get_vcpus_used(compute)
        vcpus_free = vcpus_total - vcpus_used

        if vcpus_free >= vcpu_required:
            if vcpus_total == config.CORE_COMPUTE:
                compute_list.append(f"{compute} (dedicated)")
            else:
                compute_list.append(compute)

    unique_compute_set = set(compute_list)
    return jsonify({'compute_list': list(unique_compute_set)})
