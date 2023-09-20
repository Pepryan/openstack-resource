from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
import csv

app = Flask(__name__)

# Load data from aio.csv
data = pd.read_csv('aio.csv', delimiter="|")
# Filter rows where 'Host' column has NaN values
nan_rows = data[data['Host'].isna()]
# print(data)
print(nan_rows)

# Function to get vcpus_used for a host from allocation.txt
def get_vcpus_used(host):
    # vcpus_used = 0
    # allocation_file = open('allocation.txt', 'r')
    # for line in allocation_file:
    #     parts = line.strip().split()
    #     if len(parts) >= 3 and parts[2] == host:
    #         vcpus_used += int(parts[5])
    # allocation_file.close()
    # return vcpus_used
    allocation_file = open('allocation.txt', 'r')
    vcpus_used = 0

    for line in allocation_file:
        parts = line.strip().split()
        if len(parts) >= 6 and parts[1] == host:
            vcpus_used = int(parts[5]) 
            break
    allocation_file.close()
    return vcpus_used

# Function to get vcpus_ratio for a host from ratio.txt
def get_vcpus_ratio(host):
    vcpus_ratio = 0.0
    ratio_file = open('ratio.txt', 'r')
    for line in ratio_file:
        parts = line.strip().split(', ')
        if len(parts) == 3 and parts[0] == host:
            vcpus_ratio = float(parts[1])
    ratio_file.close()
    return vcpus_ratio

@app.route('/')
def index():
    source_hosts = sorted(data['Host'].unique(), key=str)
    return render_template('index.html', source_hosts=source_hosts)

@app.route('/get_source_hosts', methods=['GET'])
def get_source_hosts():
    source_hosts = sorted(data['Host'].dropna().unique(), key=str)
    return jsonify(source_hosts)

@app.route('/get_instances', methods=['GET'])
def get_instances():
    host = request.args.get('host')
    instances = data[data['Host'] == host][['Name', 'CPU']]
    instances_json = instances.to_dict(orient='records')
    return jsonify({'instances': instances_json})

@app.route('/get_destination_host_instances', methods=['GET'])
def get_destination_host_instances():
    host = request.args.get('host')
    instances = data[data['Host'] == host][['Name', 'CPU']]
    instances_json = instances.to_dict(orient='records')
    
    # Mengambil vcpus_used dan vcpus_ratio yang sesuai dengan host
    vcpus_used = get_vcpus_used(host)
    vcpus_ratio = get_vcpus_ratio(host)

    # Menghitung vcpus_total dan vcpus_free dengan benar
    vcpus_total = vcpus_ratio * 48  # core compute
    vcpus_free = vcpus_total - vcpus_used

    return jsonify({
        'instances': instances_json,
        'vcpus_total': vcpus_total,
        'vcpus_free': vcpus_free,
        'vcpus_used': vcpus_used,
    })

@app.route('/get_instance_vcpus_used', methods=['GET'])
def get_instance_vcpus_used():
    instance_name = request.args.get('name')
    instance_host = data[data['Name'] == instance_name]['Host'].values[0]
    # vcpus_ratio = get_vcpus_ratio(instance_host)
    # vcpus_used = get_vcpus_used(instance_host)
    vcpus_used_instance = int(data[data['Name'] == instance_name]['CPU'].values[0])
    return jsonify(vcpus_used_instance)

@app.route('/get_host_allocation', methods=['GET'])
def get_host_allocation():
    host = request.args.get('host')
    allocation_file = open('allocation.txt', 'r')
    vcpus_used = 0

    for line in allocation_file:
        parts = line.strip().split()
        if len(parts) >= 6 and parts[1] == host:
            vcpus_used = int(parts[5]) 
            break

    allocation_file.close()

    ratio_file = open('ratio.txt', 'r')
    vcpus_total = 0

    for line in ratio_file:
        parts = line.strip().split(', ')
        if len(parts) == 3 and parts[0] == host:
            vcpus_ratio = float(parts[1])
            # vcpus_total = int(parts[1]) * vcpus_ratio
            break

    ratio_file.close()

    # Menghitung vcpus_total sesuai dengan jumlah Core compute
    core_compute = 48  
    vcpus_total = core_compute * vcpus_ratio

    # Menghitung vcpus_free
    vcpus_free = vcpus_total - vcpus_used

    # Membuat objek dictionary dengan informasi yang ingin dikirimkan sebagai respons
    response_data = {
        'vcpus_used': vcpus_used,
        'vcpus_total': vcpus_total,
        'vcpus_free': vcpus_free,
        'vcpus_ratio': vcpus_ratio
    }

    return jsonify(response_data)  # return respons dalam format JSON

@app.route('/generate_vcpu_allocation_plot', methods=['GET'])
def generate_vcpu_allocation_plot():
    destination_host = request.args.get('destination_host')
    file_path = 'aio.csv'
    longest_string = ""
    vcpu_claimed = []
    vcpu_labels = []

    # Load CSV
    with open(file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')  # Set delimiter to "|"
        next(csvreader)  # Skip the header row
        for row in csvreader:
            if destination_host == row[10]:  # Menggunakan indeks 10 untuk kolom 'Host'
                if row[3] == 'ACTIVE' or row[3] == 'SHUTOFF':  # Menggunakan indeks 3 untuk kolom 'Status'
                    vcpu_labels.append(f"{row[3][0]}_{row[0]}__{row[2]}")  # Menggunakan indeks sesuai dengan kolom yang dibutuhkan
                    vcpu_claimed.append(int(row[11]))  # Menggunakan indeks sesuai dengan kolom 'CPU'
                    if len(f"{row[0]}__{row[2]}") > len(longest_string):
                        longest_string = f"{row[0]}__{row[2]}"

    # Load hosts from ratio.txt
    with open('ratio.txt', 'r') as ratio_file:
        for line in ratio_file:
            parts = line.strip().split(',')
            if len(parts) == 3 and parts[0] == destination_host:
                ratio_value = float(parts[1])
                host_size = 48
                host_size = host_size * ratio_value
                print("host size",host_size)
                break  # Stop searching after finding the host

    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Calculate the new size of the host square
    # vcpus_total = sum(vcpus_destination_host)
    # allocation_file = open('allocation.txt', 'r')
    # vcpus_used_total = 0

    # for line in allocation_file:
    #     parts = line.strip().split()
    #     if len(parts) >= 6 and parts[1] == destination_host:
    #         vcpus_used_total = int(parts[5]) 
    #         break

    # allocation_file.close()
    # Total number of vCPUs
    total_vcpus = sum(vcpu_claimed)
    # print(total_vcpus)
    # New size of the host square

    # Calculate the size of each small square based on the desired number of columns
    num_cols = 16
    small_square_size = host_size / num_cols

    # Calculate the number of rows based on the total number of vCPUs and desired number of columns
    num_rows = (total_vcpus + num_cols - 1) // num_cols
    # print(num_rows)
    # Calculate the total number of small squares
    total_small_squares = num_rows * num_cols

    # Create a colormap with the number of colors equal to the number of vCPUs sizes
    colors = plt.cm.get_cmap('tab20', len(vcpu_claimed))

    # Create a new figure and axis
    fig, ax = plt.subplots()

    # Initialize the starting position for drawing squares
    x_pos = 0
    y_pos = 0

    legend_handles = []
    unique_labels = set(vcpu_labels)

    # Loop through the vCPUs and draw squares
    for i, (vcpu, label) in enumerate(zip(vcpu_claimed, vcpu_labels)):
        color = colors(i)
        for _ in range(vcpu):
            rect = plt.Rectangle((x_pos, y_pos), small_square_size, small_square_size, color=color, alpha=0.7)
            ax.add_patch(rect)
            
            # Label each small square with the evaluated vcpu_claimed value
            ax.text(x_pos + small_square_size / 2, y_pos + small_square_size / 2, str(vcpu),
                    color='white', ha='center', va='center')
            
            x_pos += small_square_size
            if x_pos >= host_size:
                x_pos = 0
                y_pos += small_square_size

        if label in unique_labels:
            legend_handles.append(rect)
            unique_labels.remove(label)

    # Draw and color remaining small squares with gray
    remaining_squares = int(host_size - total_vcpus)  # Mengubah ke integer
    for _ in range(remaining_squares):
        rect = plt.Rectangle((x_pos, y_pos), small_square_size, small_square_size, color='gray', alpha=0.7)
        ax.add_patch(rect)
        x_pos += small_square_size
        if x_pos >= host_size:
            x_pos = 0
            y_pos += small_square_size

    # Set aspect ratio to equal, so squares are not distorted
    ax.set_aspect('equal', adjustable='box')

    # Set axis limits and labels
    ax.set_xlim(0, host_size)
    ax.set_ylim(0, host_size)
    # ax.set_xlabel('vCPU')
    # ax.set_ylabel('vCPU')

    # Set custom tick intervals and labels for x and y axes
    ax.set_xticks([i * small_square_size for i in range(num_cols + 1)])
    ax.set_yticks([i * small_square_size for i in range(num_rows + 1)])
    ax.set_xticklabels([str(i) for i in range(num_cols + 1)])
    ax.set_yticklabels([str(i) for i in range(num_rows + 1)])

    # Create a legend using legend handles and unique labels
    # 1.6
    # (1.6 + (len(longest_string) * 0.05))
    ankor = 1.6 + (len(longest_string) * 0.03)
    print(ankor)
    if ankor > 3.3:
        ankor = 3.325
    ax.legend(handles=legend_handles, labels=vcpu_labels, loc='upper right', bbox_to_anchor=(ankor, 1))



    # Title plot
    image_path = f'static/results/{destination_host}_{current_time}.png'
    plt.title(destination_host)
    plt.savefig(image_path, bbox_inches='tight')
    print(f"{destination_host} exported as {image_path}")

    # Return the image path to be displayed in the HTML
    # return f"results/{destination_host}.png"
    # Return JSON response containing vCPU claimed from destination and to move
    response_data = {
        'image_path': f"static/results/{destination_host}_{current_time}.png",
        # 'vcpu_claimed_destination': vcpu_claimed_destination,
        # 'vcpu_claimed_to_move': vcpu_claimed_to_move
    }
    return jsonify(response_data)
    # return send_file(image_path, as_attachment=True)

@app.route('/list_all_instances', methods=['GET'])
def list_all_instances():
    aio_csv_path = 'aio.csv'
    aio_odc_csv_path = 'aio_odc.csv'

    # Ambil data waktu terakhir modifikasi
    aio_last_updated = os.path.getmtime(aio_csv_path)
    aio_odc_last_updated = os.path.getmtime(aio_odc_csv_path)

    # Ubah format waktu jika perlu
    aio_last_updated_str = datetime.datetime.fromtimestamp(aio_last_updated).strftime('%d-%m-%Y %H:%M:%S')
    aio_odc_last_updated_str = datetime.datetime.fromtimestamp(aio_odc_last_updated).strftime('%d-%m-%Y %H:%M:%S')

    # Load data from aio.csv
    data = pd.read_csv(aio_csv_path, delimiter="|")
    data_odc = pd.read_csv(aio_odc_csv_path, delimiter="|")

    # Convert data to a list of dictionaries
    data_list = data.to_dict(orient='records')
    data_list_odc = data_odc.to_dict(orient='records')

    return render_template('list_all_instances.html', data_list=data_list, data_list_odc=data_list_odc, aio_last_updated=aio_last_updated_str, aio_odc_last_updated=aio_odc_last_updated_str)

# @app.route('/compute_service', methods=['GET'])
# def compute_service():
#     compute_service_file = open('compute_service.txt', 'r')
#     for line in compute_service_file:
#         compute_list = []
#         parts = line.strip().split()
#         compute = print(parts[2], parts[4])
#         compute_list.append(compute)
#         # compute_service_file.close()
#     response_data = {
#         'compute_list': compute_list
#         # 'vcpu_claimed_destination': vcpu_claimed_destination,
#         # 'vcpu_claimed_to_move': vcpu_claimed_to_move
#     }
#     return jsonify(response_data)
#     # return render_template('compute_service.html')

@app.route('/get_compute_with_free_vcpus', methods=['GET'])
def get_compute_with_free_vcpus():
    vcpu_required = int(request.args.get('vcpu'))

    # Lakukan pemrosesan untuk mendapatkan daftar compute dengan vCPU gratis sesuai input
    compute_list = []

    # Contoh: Loop melalui daftar compute Anda dan periksa vCPU yang tersedia
    # Anda harus menyesuaikan logika berdasarkan data yang Anda miliki.
    for compute in data['Host']:
        vcpus_total = get_vcpus_ratio(compute) * 48  # Hitung total vCPU berdasarkan rasio
        vcpus_used = get_vcpus_used(compute)  # Dapatkan vCPU yang sudah digunakan
        vcpus_free = vcpus_total - vcpus_used  # Hitung vCPU yang tersedia
        if vcpus_free >= vcpu_required:
            compute_list.append(compute)

    # Mengonversi list ke dalam set untuk menghilangkan duplikasi
    unique_compute_set = set(compute_list)

    return jsonify({'compute_list': list(unique_compute_set)})


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, host="0.0.0.0", port=5005)
