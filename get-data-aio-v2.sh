#!/bin/bash

# Mendapatkan daftar nama proyek
project_names=($(openstack project list -c Name -f value))

# Nama file output
output_file="aio.csv"

# Menghapus file output jika sudah ada
rm -f "$output_file"

# Loop melalui setiap proyek
for project_name in "${project_names[@]}"; do
    # Membersihkan data, menggunakan delimiter "|" dan menghindari instance dengan status ERROR
    openstack server list --project "$project_name" --limit -1 --long -c ID -c Name -c Status -c "Power State" -c Networks -c "Flavor ID" -c "Flavor Name" -c "Image ID" -c "Image Name" -c Host -f csv | grep -v "ERROR" | sed 's/^"\(.*\)"$/\1/' > temp_aio_project.csv
    
    # Mengganti delimiter ke "|"
    sed -i 's/","/|/g' temp_aio_project.csv
    
    # Menghapus header
    sed -i '1d' temp_aio_project.csv
    
    # Menambahkan proyek sebagai kolom pertama
    awk -v project="$project_name" -F "|" 'BEGIN {OFS="|"} {print project, $0}' temp_aio_project.csv >> "$output_file"
done

#get flavor list
openstack flavor list -c ID -c Name -c RAM -c VCPUs -f value --all > temp_flavors_list.txt

#get id flavors from csv
cut -d '|' -f 10 aio.csv > temp_flavors_id.txt

# File input
input_file_flavors="temp_flavors_id.txt"
flavors_file="temp_flavors_list.txt"

# File output
output_file_flavors="temp_flavors_id_with_data.csv"

# Loop through each line in temp_flavors_id.csv
while IFS= read -r flavor_id; do
    # Cari ID flavor yang cocok dalam flavors_list.txt
    flavor_data=$(grep "$flavor_id" "$flavors_file")

    # Jika cocok, tambahkan data RAM dan vCPU ke baris saat ini
    if [ -n "$flavor_data" ]; then
        ram=$(echo "$flavor_data" | awk '{print $3}')
        vcpus=$(echo "$flavor_data" | awk '{print $4}')

        # Mengonversi RAM jika perlu
        if (( ram >= 1024 )); then
            ram_gb=$((ram/1024))
            ram_unit="G"
        else
            ram_gb=$ram
            ram_unit="M"
        fi

        echo "$vcpus|$ram_gb$ram_unit"
    else
        # Jika tidak ada cocokan, cetak baris saat ini tanpa perubahan
        # echo "$flavor_id"
        echo "-"
    fi
done < "$input_file_flavors" > "$output_file_flavors"

# Gabungkan aio_project.csv dan temp_flavors_id_with_data.csv
paste -d "|" "$output_file" "$output_file_flavors" > temp_combined.csv

# Tambahkan header ke file CSV
sed -i '1iProject|ID|Name|Status|Power State|Networks|Image Name|Image ID|Flavor Name|Flavor ID|Host|CPU|RAM' temp_combined.csv

# Ganti nama file menjadi aio_project.csv
mv temp_combined.csv aio.csv

# Menghapus file sementara
# rm -f temp_aio_project.csv
# rm -f temp-*
