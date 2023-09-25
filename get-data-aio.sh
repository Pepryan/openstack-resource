#!/bin/bash
source ~/admin-openrc
instance_server="172.18.218.129:~/openstack-resource"
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

# file_hosts="hosts.txt"
# for host in $(cat "$file_hosts"); do
#     ssh_result=$(ssh "$host" "sudo cat /etc/nova/nova.conf")
  
#     cpu_ratio=$(echo "$ssh_result" | grep -oP "cpu_allocation_ratio = \K\d+(\.\d+)?")

#     ram_ratio=$(echo "$ssh_result" | grep -oP "ram_allocation_ratio = \K\d+(\.\d+)?")

#     cpu_ratio=$(echo "$cpu_ratio" | sed 's/\.0$//')
#     #ram_ratio=$(echo "$ram_ratio" | sed 's/\.0$//')
#     echo "$host, $cpu_ratio, $ram_ratio"
# done > ratio.txt

scp aio.csv allocation.txt flavors.csv ubuntu@${instance_server}

# rm -f temp_*
