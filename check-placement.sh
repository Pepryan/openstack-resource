#!/bin/bash

# Source OpenStack credentials
. ~/admin-openrc

# Get token
TOKEN=$(openstack token issue -f value -c id)
echo "Token: $TOKEN"

PLACEMENTENDPOINT=$(openstack endpoint list --service placement --interface public -f value -c URL)
echo "Placement Endpoint: $PLACEMENTENDPOINT"

# Output file
output_file="placement_diff.json"

echo "[" > $output_file

# Debug resource providers
# echo "=== Debug Resource Providers ==="
curl -s -X GET "${PLACEMENTENDPOINT}/resource_providers" \
    -H "X-Auth-Token:${TOKEN}" \
    -H "Openstack-API-Version: placement latest" | jq '.' > /dev/null

openstack hypervisor list -f value -c "Hypervisor Hostname" | while read hostname; do
    # echo "=== Processing host: $hostname ==="
    
    # Get resource provider UUID for this hostname
    # echo "Getting Resource Provider UUID for $hostname..."
    provider_uuid=$(curl -s -X GET "${PLACEMENTENDPOINT}/resource_providers" \
        -H "X-Auth-Token:${TOKEN}" \
        -H "Openstack-API-Version: placement latest" | \
        jq -r ".resource_providers[] | select(.name == \"$hostname\") | .uuid")
    # echo "Provider UUID: $provider_uuid"
    
    if [ -z "$provider_uuid" ] || [ "$provider_uuid" = "null" ]; then
        echo "Warning: Could not get Provider UUID for $hostname, skipping..."
        continue
    fi
    
    # Get allocation from placement API
    # echo "Getting placement allocation..."
    curl_output=$(curl -s -X GET "${PLACEMENTENDPOINT}/resource_providers/${provider_uuid}/allocations" \
        -H "X-Auth-Token:${TOKEN}" \
        -H "Openstack-API-Version: placement latest")
    
    # Check if curl output contains error
    if echo "$curl_output" | jq -e '.errors' >/dev/null; then
        echo "Error in placement API response, skipping..."
        allocation_count=0
    else
        allocation_count=$(echo "$curl_output" | jq '[.allocations[] | .resources.VCPU] | add')
        if [ "$allocation_count" = "null" ]; then
            allocation_count=0
        fi
    fi
    # echo "Allocation Count: $allocation_count"
    
    # Get vcpu_used from openstack command
    # echo "Getting vcpu_used..."
    vcpu_used=$(openstack hypervisor show $hostname -f value -c vcpus_used)
    # echo "VCPU Used: $vcpu_used"
    
    # Compare and record if there's a mismatch
    if [ "$allocation_count" != "$vcpu_used" ]; then
        # echo "Mismatch detected, writing to file..."
        echo "{" >> $output_file
        echo "  \"hostname\": \"$hostname\"," >> $output_file
        echo "  \"placement_vcpu\": $allocation_count," >> $output_file
        echo "  \"actual_vcpu\": $vcpu_used," >> $output_file
        echo "  \"difference\": $(($allocation_count - $vcpu_used))," >> $output_file
        echo "  \"checked_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"" >> $output_file
        echo "}," >> $output_file
    fi
done

# Remove trailing comma and close JSON array
sed -i '$ s/,$//' $output_file
echo "]" >> $output_file

echo "=== Final JSON content ==="
cat $output_file

# Copy file to web server
scp $output_file ubuntu@172.18.218.129:~/openstack-resource/data/

echo "Placement check completed. Results saved to $output_file"

if [ -s "$output_file" ] && [ "$(jq length "$output_file")" -gt 0 ]; then
    echo "Found placement differences, checking instance IDs..."
    ./check-instance-ids.sh
else
    echo "No placement differences found, skipping instance ID check."
fi 