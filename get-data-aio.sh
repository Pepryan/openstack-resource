#!/bin/bash

##progress get data aio.csv
# cleansing data, use delimiter to "|", exclude instance with ERROR state
# openstack server list --all-projects --long -c ID -c Name -c Status -c "Power State" -c Networks -c "Flavor Name" -c Host --limit -1 -f csv | grep -v "ERROR" > aio.csv
# change delimiter to "|", remove double quote (")
# sed -i 's/"\([^"]*\)","\([^"]*\)","\([^"]*\)","\([^"]*\)","\([^"]*\)","\([^"]*\)","\([^"]*\)"/\1|\2|\3|\4|\5|\6|\7/' aio.csv
# get instance id to get project name
# awk -F "|" '{print $1}' aio.csv > temp-id-instance.txt
# use script to get project from id instance
# cat temp-id-instance.txt ... > temp-project-aio.txt
# add project column
# paste -d "|" temp-project-aio.txt aio.csv | sed 's/|^/|/' > aio.csv
# get vCPU and RAM, flavor name aio.csv
# awk -F "|" '{print $6}' aio.csv
# add column vCPU dan RAM
# ...
# add header to file CSV
#sed -i '1iProject|ID|Name|Status|Power State|Networks|Flavor Name|Host|CPU|RAM' aio.csv

#Cleansing data, use delimiter to "|", exclude instance with ERROR state
openstack server list --all-projects --long -c ID -c Name -c Status -c "Power State" -c Networks -c "Flavor Name" -c Host --limit -1 -f csv | grep -v "ERROR" > temp-aio.csv

#Change delimiter to "|", remove double quote (")
sed -i 's/"\([^"]*\)","\([^"]*\)","\([^"]*\)","\([^"]*\)","\([^"]*\)","\([^"]*\)","\([^"]*\)"/\1|\2|\3|\4|\5|\6|\7/' temp-aio.csv

#remove header
sed -i '1d' temp-aio.csv

#Get instance id to get project name
awk -F "|" '{print $1}' temp-aio.csv > temp-id-instance.txt

#Remove the first line from temp-id-instance.txt
# sed -i '1d' temp-id-instance.txt

instance_ids=($(cat temp-id-instance.txt))

#Loop through instance IDs
for instance_id in "${instance_ids[@]}"; do
    # Get project ID using OpenStack command
    project_id=$(openstack server show "$instance_id" -c project_id -f value)
    
    # Get project name using OpenStack command
    project_name=$(openstack project show "$project_id" -c name -f value)
    
    #echo "Instance ID: $instance_id"
    #echo "Project Name: $project_name"
    #echo "------------------------"
    echo $project_name >> temp-project-aio.txt
done

#add project column
# paste -d "|" temp-project-aio.txt temp-aio.csv | sed 's/|^/|/' > aio.csv
paste -d "|" temp-project-aio.txt temp-aio.csv > temp-aio-modified.csv

#get vCPU and RAM, flavor name aio.csv
awk -F "|" '{print $7}' temp-aio-modified.csv > temp-flavor-name.txt

# flavor_ids=($(cat temp-flavor-name.txt))
#flavor_ids=($(cat flavor-name.txt))

#Read file into an array, preserving empty lines
mapfile -t flavor_ids < temp-flavor-name.txt

# Name of the output file for vcpu flavor
output_file_vcpu="temp-vcpu-ram.txt"

# Remove the output file if it already exists
rm -f "$output_file_vcpu"

# Loop through instance IDs
for flavor_id in "${flavor_ids[@]}"; do
    # Trim leading and trailing whitespace from the flavor_id
    trimmed_flavor_id=$(echo "$flavor_id" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
    
    # Check if the trimmed flavor_id is empty
    if [[ -z "$trimmed_flavor_id" ]]; then
        # If it's empty, add an empty line to the output
        echo >> "$output_file_vcpu"
    else
        # If it's not empty, retrieve flavor info and process it
        flavor_info=$(openstack flavor show "$trimmed_flavor_id" -f json)

        # Parse RAM and vCPU information from the flavor
        ram=$(echo "$flavor_info" | jq -r '.ram')
        vcpus=$(echo "$flavor_info" | jq -r '.vcpus')

        if (( ram >= 1024 )); then
            ram_gb=$((ram/1024))
            ram_unit="G"
        else
            ram_gb=$ram
            ram_unit="M"
        fi

        echo "$vcpus, ${ram_gb}${ram_unit}" >> "$output_file_vcpu"
    fi
done

#replace , with |
sed 's/, /|/g' temp-vcpu-ram.txt > temp-vcpu-ram-modified.txt

#combine file
paste -d "|" temp-aio-modified.csv temp-vcpu-ram-modified.txt | awk -F '|' '{print $1 "|" $2 "|" $3 "|" $4 "|" $5 "|" $6 "|" $7 "|" $8 "|" $9 "|" $10}' > aio.csv

#remove header and change header csv
# sed -i '1d' aio.csv
sed -i '1iProject|ID|Name|Status|Power State|Networks|Flavor Name|Host|CPU|RAM' aio.csv

#remove junk files
# rm -rf temp-*