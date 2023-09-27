from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
import csv

app = Flask(__name__)
data = pd.read_csv('data/aio.csv', delimiter="|")
nan_rows = data[data['Host'].isna()]
# print(nan_rows)

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

if __name__ == '__main__':    
    app.run(debug=True, host="0.0.0.0", port=5005)
