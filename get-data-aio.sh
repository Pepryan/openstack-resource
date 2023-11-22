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
openstack volume list --all-projects -f json > volumes.json

### ODC (because error when volume list --all-projects)
# # Membuat file JSON kosong
# echo "" > volumes.json

# # Mendapatkan daftar project
# project_list=$(openstack project list -f value -c ID)

# # Melakukan loop melalui setiap project
# for project_id in $project_list; do
#     # Mendapatkan daftar volume untuk project saat ini dan menambahkannya ke file JSON
#     if openstack volume list --project $project_id -f json | jq -e '. | length > 0' > /dev/null; then
#         openstack volume list --project $project_id -f json > volumes-$project_id.json
#         sed -i '1d' volumes-$project_id.json
#         sed -i '$d' volumes-$project_id.json  # Menghapus baris terakhir
#         sed -i '$d' volumes-$project_id.json  # Menghapus baris terakhir lagi
#         echo "}," >> volumes-$project_id.json
#         cat volumes-$project_id.json >> volumes-all-project.json
#     # else
#         # echo ""
#         # echo "Skipping project $project_id as it has no volumes."
#         # no volumes
#         # volumes-095f7c918dd94ce39ef5374e90eb2419.json
#         # volumes-21078c1bf3b148bbbeda74ba5a2ef77f.json
#         # volumes-b4c0f99260ae41d3ab7cb3b88811b697.json
#         # volumes-cb0d55d804d24bd9aa47c5560f942fc4.json
#     fi
# done

# mv volumes-all-project.json volumes.json
# rm -f volumes-*.json
# sed -i '1s/^/\[/;1!b' volumes.json
# sed -i '$d' volumes.json  # Menghapus baris terakhir
# # sed -i '$d' volumes.json  # Menghapus baris terakhir lagi
# echo "}" >> volumes.json
# echo "]" >> volumes.json


scp aio.csv allocation.txt flavors.csv ratio.txt cephdf.txt volumes.json ubuntu@${instance_server}
ssh ubuntu@${instance_server} sudo systemctl restart openstack-resource

# rm -f temp_*
