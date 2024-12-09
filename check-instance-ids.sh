#!/bin/bash
source ~/admin-openrc

# Get token and placement endpoint
TOKEN=$(openstack token issue -f value -c id)
PLACEMENTENDPOINT=$(openstack endpoint list --service placement --interface public -f value -c URL)

# Output file
output_file="instance_ids_check.json"
echo "[" > "$output_file"

# Get all resource providers in one call
# echo "Getting all resource providers..."
all_providers=$(curl -s -X GET "${PLACEMENTENDPOINT}/resource_providers" \
    -H "X-Auth-Token:${TOKEN}" \
    -H "Openstack-API-Version: placement latest")

# Read compute nodes from placement_diff.json
# echo "Reading compute nodes with placement differences..."
compute_nodes=$(jq -r '.[].hostname' placement_diff.json)

# echo "Found compute nodes to check: $compute_nodes"

for hostname in $compute_nodes; do
    # echo "=== Processing host: $hostname ==="
    
    provider_uuid=$(echo "$all_providers" | jq -r ".resource_providers[] | select(.name == \"$hostname\") | .uuid")
    
    if [ -z "$provider_uuid" ] || [ "$provider_uuid" = "null" ]; then
        echo "Warning: No provider UUID found for $hostname"
        continue
    fi
    
    # echo "Provider UUID: $provider_uuid"
    
    # Get IDs from placement API
    # echo "Getting placement allocations..."
    curl_output=$(curl -s -X GET "${PLACEMENTENDPOINT}/resource_providers/${provider_uuid}/allocations" \
        -H "X-Auth-Token:${TOKEN}" \
        -H "Openstack-API-Version: placement latest")
    
    if echo "$curl_output" | jq -e '.errors' >/dev/null; then
        echo "Error in placement API response for $hostname"
        continue
    fi
    
    curl_ids=$(echo "$curl_output" | jq -r '.allocations | keys[]')
    
    # Get IDs directly from openstack command for this host
    # echo "Getting instances from OpenStack for host $hostname..."
    openstack_ids=$(openstack server list --all-projects --host "$hostname" -f value -c ID)
    
    # Convert to arrays
    IFS=$'\n' read -r -d '' -a curl_array <<< "$curl_ids"
    IFS=$'\n' read -r -d '' -a openstack_array <<< "$openstack_ids"
    
    # echo "Found ${#curl_array[@]} instances in placement"
    # echo "Found ${#openstack_array[@]} instances in OpenStack"
    
    # Find differences
    missing_in_openstack=()
    missing_in_curl=()
    
    for id in "${curl_array[@]}"; do
        if [[ ! " ${openstack_array[*]} " =~ " ${id} " ]]; then
            missing_in_openstack+=("$id")
        fi
    done
    
    for id in "${openstack_array[@]}"; do
        if [[ ! " ${curl_array[*]} " =~ " ${id} " ]]; then
            missing_in_curl+=("$id")
        fi
    done
    
    # Write to JSON if there are differences
    if [ ${#missing_in_openstack[@]} -gt 0 ] || [ ${#missing_in_curl[@]} -gt 0 ]; then
        echo "Found differences for $hostname"
        echo "Missing in OpenStack: ${missing_in_openstack[*]}"
        echo "Missing in Placement: ${missing_in_curl[*]}"
        
        {
            echo "{"
            echo "  \"hostname\": \"$hostname\","
            echo "  \"missing_in_openstack\": [$(printf '"%s",' "${missing_in_openstack[@]}" | sed 's/,$//' || echo '')],"
            echo "  \"missing_in_curl\": [$(printf '"%s",' "${missing_in_curl[@]}" | sed 's/,$//' || echo '')],"
            echo "  \"checked_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\""
            echo "},"
        } >> "$output_file"
    else
        echo "No instance ID differences found for $hostname"
    fi
done

# Remove trailing comma and close JSON array
sed -i '$ s/,$//' "$output_file"
echo "]" >> "$output_file"

echo "Copying file to web server..."
scp "$output_file" ubuntu@172.18.218.129:~/openstack-resource/data/

echo "Check completed. Results saved to $output_file"
