import pandas as pd
import os
import json
import re
# import numpy as np

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

def extract_cephdf_data():
    # Initialize variables to store the extracted values
    total = avail = raw_used = raw_used_percentage = "N/A"

    # Open the file and read it line by line
    with open("data/cephdf.txt", "r") as file:
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
    # print(total, avail, raw_used, raw_used_percentage)
    # Return the extracted values as a dictionary
    return {
        "Total": total,
        "Avail": avail,
        "Raw Used": raw_used,
        "%Raw Used": raw_used_percentage
    }

def update_or_add_reserved_data(data, compute_name, cpu, ram, kebutuhan):
    if compute_name not in data:
        data[compute_name] = {}
    if cpu:
        data[compute_name]['CPU'] = cpu
    if ram:
        data[compute_name]['RAM'] = ram
    if kebutuhan:
        data[compute_name]['Kebutuhan'] = kebutuhan

def get_sorted_computes():
    with open('data/ratio.txt', 'r') as file:
        lines = file.readlines()
        compute_names = [line.split(',')[0].strip() for line in lines]

    sorted_computes = sorted(compute_names)
    # print(sorted_computes)
    return sorted_computes