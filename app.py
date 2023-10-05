from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import matplotlib.pyplot as plt
# import numpy as np
import datetime
import os
import csv
import json

app = Flask(__name__)
data = pd.read_csv('data/aio.csv', delimiter="|")
nan_rows = data[data['Host'].isna()]
# print(nan_rows)

# reserved_data_file = 'data/reserved_data.json'

class DataHost:
    @staticmethod
    def get_vcpus_used(host):
        allocation_file = open('data/allocation.txt', 'r')
        vcpus_used = 0
        for line in allocation_file:
            parts = line.strip().split()
            if len(parts) >= 6 and parts[1] == host:
                vcpus_used = int(parts[5]) 
                break
        allocation_file.close()
        return vcpus_used

    @staticmethod
    def get_vcpus_ratio(host):
        vcpus_ratio = 0.0
        ratio_file = open('data/ratio.txt', 'r')
        for line in ratio_file:
            parts = line.strip().split(', ')
            if len(parts) == 3 and parts[0] == host:
                vcpus_ratio = float(parts[1])
        ratio_file.close()
        return vcpus_ratio

class Formatter:
    @staticmethod
    def format_ram(ram):
        if ram >= 1024:
            return str(ram // 1024) + 'G'
        else:
            return str(ram) + 'M'
        
    @staticmethod
    def format_public(is_public):
        return 'Yes' if is_public else 'No'
        
    @staticmethod
    def format_swap(swap):
        if swap >= 1024:
            swap = int(swap)
            return str(swap // 1024) + 'G'
        elif swap < 1024:
            swap = int(swap)
            return str(swap) + 'M'
        else:
            return '-'
        
    @staticmethod
    def format_properties(properties):
        return '-' if pd.isna(properties) else properties
    
def calculate_total_capacity_allocation_ratio(ratio, formatted_data):
    total_capacity = 0
    total_capacity_memory = 0

    # Loop melalui data yang telah diformat sebelumnya
    for item in formatted_data:
        vcpus_ratio = item['vCPUs Ratio']
        compute_name = item['Compute Name']

        # Cek apakah host/compute memiliki rasio yang sesuai
        if vcpus_ratio == ratio:
            vcpus_capacity = item['VCPUs']['Capacity']
            total_capacity += vcpus_capacity

            memory_capacity = item['Memory']['Capacity']
            total_capacity_memory += memory_capacity

    return total_capacity, total_capacity_memory

def calculate_total_usage_allocation_ratio(ratio, formatted_data):
    total_usage = 0
    total_usage_memory = 0

    # Loop melalui data yang telah diformat sebelumnya
    for item in formatted_data:
        vcpus_ratio = item['vCPUs Ratio']
        compute_name = item['Compute Name']

        # Cek apakah host/compute memiliki rasio yang sesuai
        if vcpus_ratio == ratio:
            vcpus_usage = item['VCPUs']['Used']
            total_usage += vcpus_usage

            memory_usage = item['Memory']['Used']
            total_usage_memory += memory_usage

    return total_usage, total_usage_memory

def calculate_total_available_allocation_ratio(ratio, formatted_data):
    total_capacity, total_capacity_memory = calculate_total_capacity_allocation_ratio(ratio, formatted_data)
    total_usage, total_usage_memory = calculate_total_usage_allocation_ratio(ratio, formatted_data)
    total_available = total_capacity - total_usage
    total_available_memory = total_capacity_memory - total_usage_memory

    return total_available, total_available_memory

# Fungsi untuk membaca data dari reserved.json
def read_reserved_data():
    reserved_data_file = 'data/reserved.json'
    reserved_data = {}

    if os.path.exists(reserved_data_file):
        with open(reserved_data_file, 'r') as f:
            try:
                reserved_data = json.load(f)
            except json.decoder.JSONDecodeError:
                # Tangani jika file JSON kosong atau tidak valid
                reserved_data = {}

    return reserved_data

# Fungsi untuk menghitung total reserved untuk suatu rasio alokasi
def calculate_total_reserved_allocation_ratio(ratio, formatted_data, reserved_data):
    total_reserved = 0
    total_reserved_memory = 0

    for item in formatted_data:
        vcpus_ratio = item['vCPUs Ratio']
        compute_name = item['Compute Name']

        if vcpus_ratio == ratio:
            # Cek apakah host/compute memiliki rasio yang sesuai
            if compute_name in reserved_data:
                reserved_item = reserved_data[compute_name]
                if reserved_item['CPU']:
                    total_reserved += int(reserved_item['CPU'])
                if reserved_item['RAM']:
                    total_reserved_memory += int(reserved_item['RAM']) * 1024  # Konversi dari GB ke MB

    return total_reserved, total_reserved_memory

def calculate_total_maintenance_allocation_ratio(ratio, formatted_data, reserved_data):
    total_maintenance = 0
    total_maintenance_memory = 0

    for item in formatted_data:
        vcpus_ratio = item['vCPUs Ratio']
        compute_name = item['Compute Name']

        if vcpus_ratio == ratio:
            # Cek apakah host/compute memiliki rasio yang sesuai
            if compute_name in reserved_data:
                reserved_item = reserved_data[compute_name]
                kebutuhan = reserved_item.get('Kebutuhan', '')

                # Periksa apakah ada kebutuhan "Backup for maintenance" (case insensitive)
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



def update_or_add_reserved_data(data, compute_name, cpu, ram, kebutuhan):
    if compute_name not in data:
        data[compute_name] = {}
    if cpu:
        data[compute_name]['CPU'] = cpu
    if ram:
        data[compute_name]['RAM'] = ram
    if kebutuhan:
        data[compute_name]['Kebutuhan'] = kebutuhan

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
    vcpus_used = DataHost.get_vcpus_used(host)
    vcpus_ratio = DataHost.get_vcpus_ratio(host)    
    vcpus_total = vcpus_ratio * 48  
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
    vcpus_used_instance = int(data[data['Name'] == instance_name]['CPU'].values[0])
    return jsonify(vcpus_used_instance)

@app.route('/get_host_allocation', methods=['GET'])
def get_host_allocation():
    host = request.args.get('host')
    vcpus_used = 0
    vcpus_total = 0
    vcpus_used = DataHost.get_vcpus_used(host)
    vcpus_ratio = DataHost.get_vcpus_ratio(host)
    
    core_compute = 48  
    vcpus_total = core_compute * vcpus_ratio
    vcpus_free = vcpus_total - vcpus_used
    
    response_data = {
        'vcpus_used': vcpus_used,
        'vcpus_total': vcpus_total,
        'vcpus_free': vcpus_free,
        'vcpus_ratio': vcpus_ratio
    }
    return jsonify(response_data)

@app.route('/generate_vcpu_allocation_plot', methods=['GET'])
def generate_vcpu_allocation_plot():
    destination_host = request.args.get('destination_host')
    file_path = 'data/aio.csv'
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
    
    with open('data/ratio.txt', 'r') as ratio_file:
        for line in ratio_file:
            parts = line.strip().split(',')
            if len(parts) == 3 and parts[0] == destination_host:
                ratio_value = float(parts[1])
                host_size = 48
                host_size = host_size * ratio_value
                print("host size",host_size)
                break  
    
    total_vcpus = sum(vcpu_claimed)
    num_cols = 16
    small_square_size = host_size / num_cols
    num_rows = (total_vcpus + num_cols - 1) // num_cols
    # total_small_squares = num_rows * num_cols
    
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
    print(ankor)
    if ankor > 3.3:
        ankor = 3.325
    ax.legend(handles=legend_handles, labels=vcpu_labels, loc='upper right', bbox_to_anchor=(ankor, 1))

    image_path = f'static/results/{destination_host}.png'
    plt.title(destination_host)
    plt.savefig(image_path, bbox_inches='tight')
    print(f"{destination_host} exported as {image_path}")
    
    response_data = {
        'image_path': f"static/results/{destination_host}.png",
    }
    return jsonify(response_data)
    
@app.route('/list_all_instances', methods=['GET'])
def list_all_instances():
    aio_csv_path = 'data/aio.csv'
    aio_last_updated = os.path.getmtime(aio_csv_path)
    aio_last_updated_str = datetime.datetime.fromtimestamp(aio_last_updated).strftime('%d-%m-%Y %H:%M:%S')
    
    data = pd.read_csv(aio_csv_path, delimiter="|")

    data_list = data.to_dict(orient='records')

    for instance in data_list:
        for key, value in instance.items():
            if pd.isna(value) or value == '':
                instance[key] = '-'
    return render_template('list_all_instances.html', data_list=data_list, aio_last_updated=aio_last_updated_str)

@app.route('/get_compute_with_free_vcpus', methods=['GET'])
def get_compute_with_free_vcpus():
    vcpu_required = int(request.args.get('vcpu'))
    
    compute_list = []
    for compute in data['Host']:
        vcpus_total = DataHost.get_vcpus_ratio(compute) * 48  
        vcpus_used = DataHost.get_vcpus_used(compute)  
        vcpus_free = vcpus_total - vcpus_used  
        
        if vcpus_free >= vcpu_required:
            if vcpus_total == 48:
                compute_list.append(f"{compute} (dedicated)")  
            else:
                compute_list.append(compute)
    
    unique_compute_set = set(compute_list)
    return jsonify({'compute_list': list(unique_compute_set)})

@app.route('/list_all_flavors', methods=['GET'])
def list_all_flavors():
    flavor_data = pd.read_csv('data/flavors.csv', delimiter='|')
    flavor_last_updated = os.path.getmtime('data/flavors.csv')
    flavor_last_updated_str = datetime.datetime.fromtimestamp(flavor_last_updated).strftime('%d-%m-%Y %H:%M:%S')
    
    formatter = Formatter()
    flavor_data['RAM'] = flavor_data['RAM'].apply(formatter.format_ram)
    flavor_data['Is Public'] = flavor_data['Is Public'].apply(formatter.format_public)
    flavor_data['Swap'] = flavor_data['Swap'].apply(formatter.format_swap)
    flavor_data['Properties'] = flavor_data['Properties'].apply(formatter.format_properties)
    
    flavor_data = flavor_data.to_dict(orient='records')
    return render_template('list_all_flavors.html', flavor_data=flavor_data, flavor_last_updated=flavor_last_updated_str)

@app.route('/allocation')
def allocation():
    with open('data/allocation.txt', 'r') as allocation_file:
        allocation_data = allocation_file.readlines()

    with open('data/ratio.txt', 'r') as ratio_file:
        ratio_data = ratio_file.readlines()

    first_line = ratio_data[0].strip()
    site_name = first_line.split('-')[0].upper()

    allocation_last_updated = os.path.getmtime('data/allocation.txt')
    allocation_last_updated_str = datetime.datetime.fromtimestamp(allocation_last_updated).strftime('%d-%m-%Y %H:%M:%S')

    formatted_data = []

    for allocation_line, ratio_line in zip(allocation_data, ratio_data):
        allocation_parts = allocation_line.strip().split()
        ratio_parts = ratio_line.strip().split()
        if len(allocation_parts) >= 6 and len(ratio_parts) >= 3:
            compute_name = allocation_parts[1]
            vcpus_used = int(allocation_parts[5])
            vcpus_ratio = DataHost.get_vcpus_ratio(compute_name)
            core = 48
            vcpus_capacity = int(vcpus_ratio * 48)
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

            # Hitung Availability After Reservation untuk CPU
            if reserved_item['CPU']:
                cpu_availability_after_reservation = vcpus_capacity - vcpus_used - int(reserved_item['CPU'])
            else:
                cpu_availability_after_reservation = vcpus_capacity - vcpus_used

            # Hitung Availability After Reservation untuk RAM
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
    
    total_capacity_1_1, total_capacity_memory_1_1 = calculate_total_capacity_allocation_ratio('1:1', formatted_data)
    total_capacity_1_4, total_capacity_memory_1_4 = calculate_total_capacity_allocation_ratio('1:4', formatted_data)
    total_capacity_1_8, total_capacity_memory_1_8 = calculate_total_capacity_allocation_ratio('1:8', formatted_data)

    total_usage_1_1, total_usage_memory_1_1 = calculate_total_usage_allocation_ratio('1:1', formatted_data)
    total_usage_1_4, total_usage_memory_1_4 = calculate_total_usage_allocation_ratio('1:4', formatted_data)
    total_usage_1_8, total_usage_memory_1_8 = calculate_total_usage_allocation_ratio('1:8', formatted_data)

    total_available_1_1, total_available_memory_1_1 = calculate_total_available_allocation_ratio('1:1', formatted_data)
    total_available_1_4, total_available_memory_1_4 = calculate_total_available_allocation_ratio('1:4', formatted_data)
    total_available_1_8, total_available_memory_1_8 = calculate_total_available_allocation_ratio('1:8', formatted_data)

    percentage_total_capacity_1_1 = round((total_capacity_1_1 / total_capacity_1_1) * 100, 2)
    percentage_total_usage_1_1 = round((total_usage_1_1 / total_capacity_1_1) * 100, 2)
    percentage_total_available_1_1 = round((total_available_1_1 / total_capacity_1_1) * 100, 2)

    total_usage_shared = total_usage_1_4 + total_usage_1_8
    total_available_shared = total_available_1_4 + total_available_1_8
    total_capacity_shared = total_capacity_1_4 + total_capacity_1_8
    percentage_total_capacity_shared = 100
    percentage_total_usage_shared = round((total_usage_shared / total_capacity_shared) * 100, 2)
    percentage_total_available_shared = round((total_available_shared / total_capacity_shared) * 100, 2)

    # Hitung Total Reserved untuk Dedicated (1:1)
    total_reserved_1_1, total_reserved_memory_1_1 = calculate_total_reserved_allocation_ratio('1:1', formatted_data, reserved_data)

    # Hitung Total Reserved untuk Shared (1:4)
    total_reserved_1_4, total_reserved_memory_1_4 = calculate_total_reserved_allocation_ratio('1:4', formatted_data, reserved_data)

    # Hitung Total Reserved untuk Shared (1:8)
    total_reserved_1_8, total_reserved_memory_1_8 = calculate_total_reserved_allocation_ratio('1:8', formatted_data, reserved_data)

    total_reserved_memory_all = round((total_reserved_memory_1_1 + total_reserved_memory_1_4 + total_reserved_memory_1_8) / 1048576, 2)

    # Hitung Total Maintenance untuk Dedicated (1:1)
    total_maintenance_1_1, total_maintenance_memory_1_1 = calculate_total_maintenance_allocation_ratio('1:1', formatted_data, reserved_data)

    # Hitung Total Maintenance untuk Shared (1:4)
    total_maintenance_1_4, total_maintenance_memory_1_4 = calculate_total_maintenance_allocation_ratio('1:4', formatted_data, reserved_data)

    # Hitung Total Maintenance untuk Shared (1:8)
    total_maintenance_1_8, total_maintenance_memory_1_8 = calculate_total_maintenance_allocation_ratio('1:8', formatted_data, reserved_data)

    total_maintenance_memory_all = round((total_maintenance_memory_1_1 + total_maintenance_memory_1_4 + total_maintenance_memory_1_8) / 1048576, 2)

    total_available_final_1_1 = total_available_1_1 - total_reserved_1_1 - total_maintenance_1_1
    total_available_final_1_4 = total_available_1_4 - total_reserved_1_4 - total_maintenance_1_4
    total_available_final_1_8 = total_available_1_8 - total_reserved_1_8 - total_maintenance_1_8

    total_capacity_memory_all = round((total_capacity_memory_1_1 + total_capacity_memory_1_4 + total_capacity_memory_1_8) / 1048576, 2)
    total_usage_memory_all = round((total_usage_memory_1_1 + total_usage_memory_1_4 + total_usage_memory_1_8) / 1048576, 2)
    total_available_memory_all = round((total_available_memory_1_1 + total_available_memory_1_4 + total_available_memory_1_8) / 1048576, 2)

    total_available_memory_final = round(total_available_memory_all - total_reserved_memory_all - total_maintenance_memory_all, 2)

    # return render_template('allocation.html', data=formatted_data, allocation_last_updated=allocation_last_updated_str)

    return render_template('allocation.html', data=formatted_data, site_name=site_name,allocation_last_updated=allocation_last_updated_str, 
    
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
    total_available_memory_final=total_available_memory_final

    )

@app.route('/save_reserved', methods=['POST'])
def save_reserved():
    try:
        data = request.get_json()

        # Pastikan 'data' memiliki format yang sesuai
        if not isinstance(data, dict):
            raise ValueError("Data tidak valid.")

        reserved_data_file = 'data/reserved.json'
        reserved_data = {}

        # Baca data JSON yang sudah ada (jika ada)
        if os.path.exists(reserved_data_file):
            with open(reserved_data_file, 'r') as f:
                try:
                    reserved_data = json.load(f)
                except json.decoder.JSONDecodeError:
                    # Tangani jika file JSON kosong atau tidak valid
                    reserved_data = {}

        for compute_name, compute_data in data.items():
            cpu = compute_data.get('CPU', '') 
            ram = compute_data.get('RAM', '')  # Memberikan nilai default "" jika key tidak ada
            kebutuhan = compute_data.get('Kebutuhan', '')

            # Jika key tidak ada dalam data komputer, tambahkan dengan nilai kosong
            if compute_name not in reserved_data:
                reserved_data[compute_name] = {"CPU": "", "RAM": "", "Kebutuhan": ""}

            # Perbarui atau tambahkan data sesuai dengan nama komputer
            reserved_data[compute_name]["CPU"] = cpu
            reserved_data[compute_name]["RAM"] = ram
            reserved_data[compute_name]["Kebutuhan"] = kebutuhan

        # Simpan data ke dalam file JSON
        with open(reserved_data_file, 'w') as f:
            json.dump(reserved_data, f, indent=4)

        return jsonify({"success": True}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

#         # Redirect kembali ke halaman /allocation
#         return redirect('/allocation')
#     else:
#         return 'Method not allowed', 405


if __name__ == '__main__':    
    app.run(debug=True, host="0.0.0.0", port=5005)
