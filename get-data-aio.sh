#!/bin/bash
source ~/admin-openrc
instance_server="172.18.218.129:~/openstack-resource/data"
project_names=($(openstack project list -c Name -f value))
output_file="aio.csv"

rm -f "$output_file"

for project_name in "${project_names[@]}"; do
    openstack server list --project "$project_name" --limit -1 --long -c ID -c Name -c Status -c "Power State" -c Networks -c "Flavor ID" -c "Flavor Name" -c "Image ID" -c "Image Name" -c Host -f csv | grep -v "ERROR" | sed 's/^"\(.*\)"$/\1/' > temp_aio_project.csv

    sed -i 's/","/|/g' temp_aio_project.csv

    sed -i '1d' temp_aio_project.csv

    awk -v project="$project_name" -F "|" 'BEGIN {OFS="|"} {print project, $0}' temp_aio_project.csv >> "$output_file"
done

openstack flavor list -c ID -c Name -c RAM -c VCPUs -f value --all > temp_flavors_list.txt

#get id flavors from csv
cut -d '|' -f 10 aio.csv > temp_flavors_id.txt

input_file_flavors="temp_flavors_id.txt"
flavors_file="temp_flavors_list.txt"

output_file_flavors="temp_flavors_id_with_data.csv"

while IFS= read -r flavor_id; do
    if [ "$flavor_id" == "dde4a158-8e79-43bf-a7f7-c8b6db17b3d3" ]
    then
        echo "4|16G"
    else
        flavor_data=$(grep "$flavor_id" "$flavors_file")

        if [ -n "$flavor_data" ]; then
            ram=$(echo "$flavor_data" | awk '{print $3}')
            vcpus=$(echo "$flavor_data" | awk '{print $4}')

            if (( ram >= 1024 )); then
                ram_gb=$((ram/1024))
                ram_unit="G"
            else
                ram_gb=$ram
                ram_unit="M"
            fi

            # echo "$vcpus|$ram ($ram_gb $ram_unit)"
            echo "$vcpus|$ram_gb$ram_unit"
        else
            # echo "$flavor_id"
            echo "-"
        fi
    fi
done < "$input_file_flavors" > "$output_file_flavors"


paste -d "|" "$output_file" "$output_file_flavors" > temp_combined.csv

sed -i '1iProject|ID|Name|Status|Power State|Networks|Image Name|Image ID|Flavor Name|Flavor ID|Host|CPU|RAM' temp_combined.csv

mv temp_combined.csv aio.csv

openstack hypervisor list --long -f value > allocation.txt

# openstack compute service list --long -f value > compute_service.txt

openstack flavor list --all --long -f value | sed 's/ /|/g' | sed 's/,|/, /g' > flavors.csv
sed -i '1iID|Name|RAM|Disk|Ephemeral|VCPUs|Is Public|Swap|RXTX Factor|Properties' flavors.csv

openstack hypervisor list -c "Hypervisor Hostname" -f value > temp_hosts.txt
file_hosts='temp_hosts.txt'

for host in $(cat "$file_hosts"); do
    ssh_result=$(ssh "$host" "sudo cat /etc/nova/nova.conf")

    cpu_ratio=$(echo "$ssh_result" | grep -oP "cpu_allocation_ratio = \K\d+(\.\d+)?")
    ram_ratio=$(echo "$ssh_result" | grep -oP "ram_allocation_ratio = \K\d+(\.\d+)?")

    cpu_ratio=$(echo "$cpu_ratio" | sed 's/\.0$//')
    #ram_ratio=$(echo "$ram_ratio" | sed 's/\.0$//')
    echo "$host, $cpu_ratio, $ram_ratio"
done > ratio.txt

ceph df > cephdf.txt

### GTI
# Membuat file JSON kosong untuk semua volume
echo "[]" > volumes_all_project.json

# Mendapatkan daftar project
project_list=$(openstack project list -f value -c ID -c Name)

# Melakukan loop melalui setiap project
while read -r project_id project_name; do
    echo "Processing project: $project_name ($project_id)"

    # Mendapatkan daftar volume untuk project saat ini
    openstack volume list --project $project_id -f json > volumes-$project_id.json

    # Periksa apakah ada volume dalam project ini
    if [ -s volumes-$project_id.json ] && [ "$(cat volumes-$project_id.json)" != "[]" ]; then
        echo "Found volumes for project $project_name"

        # Tambahkan nama project ke setiap volume
        python3 - <<EOF
import json

# Load volumes for this project
with open('volumes-$project_id.json', 'r') as f:
    volumes = json.load(f)

# Add project name to each volume
for volume in volumes:
    volume['Project'] = "$project_name"

# Save updated volumes
with open('volumes-$project_id.json', 'w') as f:
    json.dump(volumes, f)
EOF

        # Gabungkan dengan file semua project
        python3 - <<EOF
import json

# Load existing volumes
with open('volumes_all_project.json', 'r') as f:
    all_volumes = json.load(f)

# Load volumes for this project
with open('volumes-$project_id.json', 'r') as f:
    project_volumes = json.load(f)

# Append project volumes to all volumes
all_volumes.extend(project_volumes)

# Save updated all volumes
with open('volumes_all_project.json', 'w') as f:
    json.dump(all_volumes, f, indent=2)
EOF
    else
        echo "No volumes found for project $project_name"
    fi
done <<< "$(echo "$project_list")"

# Pindahkan file final ke volumes.json
mv volumes_all_project.json volumes.json
rm -f volumes-*.json

### ODC (because error when volume list --all-projects)
# # Membuat file JSON kosong untuk semua volume
# echo "[]" > volumes_all_project.json
#
# # Mendapatkan daftar project
# project_list=$(openstack project list -f value -c ID -c Name)
#
# # Melakukan loop melalui setiap project
# while read -r project_id project_name; do
#     echo "Processing project: $project_name ($project_id)"
#
#     # Mendapatkan daftar volume untuk project saat ini
#     openstack volume list --project $project_id -f json > volumes-$project_id.json
#
#     # Periksa apakah ada volume dalam project ini
#     if [ -s volumes-$project_id.json ] && [ "$(cat volumes-$project_id.json)" != "[]" ]; then
#         echo "Found volumes for project $project_name"
#
#         # Tambahkan nama project ke setiap volume
#         python3 - <<EOF
# import json
#
# # Load volumes for this project
# with open('volumes-$project_id.json', 'r') as f:
#     volumes = json.load(f)
#
# # Add project name to each volume
# for volume in volumes:
#     volume['Project'] = "$project_name"
#
# # Save updated volumes
# with open('volumes-$project_id.json', 'w') as f:
#     json.dump(volumes, f)
# EOF
#
#         # Gabungkan dengan file semua project
#         python3 - <<EOF
# import json
#
# # Load existing volumes
# with open('volumes_all_project.json', 'r') as f:
#     all_volumes = json.load(f)
#
# # Load volumes for this project
# with open('volumes-$project_id.json', 'r') as f:
#     project_volumes = json.load(f)
#
# # Append project volumes to all volumes
# all_volumes.extend(project_volumes)
#
# # Save updated all volumes
# with open('volumes_all_project.json', 'w') as f:
#     json.dump(all_volumes, f, indent=2)
# EOF
#     else
#         echo "No volumes found for project $project_name"
#     fi
# done <<< "$(echo "$project_list")"
#
# # Pindahkan file final ke volumes.json
# mv volumes_all_project.json volumes.json
# rm -f volumes-*.json


scp aio.csv allocation.txt flavors.csv ratio.txt cephdf.txt volumes.json ubuntu@${instance_server}

ip_address=$(echo $instance_server | cut -d ':' -f 1)
instance_server="$ip_address"

# Get the directory where the script is located
#SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run placement check using absolute path
#echo "Running placement allocation check..."
. /home/ubuntu/workdir/scripts/openstack-resource/check-placement.sh

ssh ubuntu@${instance_server} "sudo systemctl restart openstack-resource.service"

# rm -f temp_*
