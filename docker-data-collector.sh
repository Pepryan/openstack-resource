#!/bin/bash
# This script is designed to be run on the OpenStack server to collect data
# and transfer it to the Docker container

# Source OpenStack credentials
source ~/admin-openrc

# Set the Docker container's data directory
CONTAINER_DATA_DIR="/app/data"
CONTAINER_NAME="openstack-resource"

# Check if the container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "Error: Container $CONTAINER_NAME is not running"
    exit 1
fi

# Run the original data collection script
echo "Collecting OpenStack resource data..."
./get-data-aio.sh

# Copy the data files to the Docker container
echo "Copying data files to Docker container..."
docker cp data/aio.csv $CONTAINER_NAME:$CONTAINER_DATA_DIR/
docker cp data/allocation.txt $CONTAINER_NAME:$CONTAINER_DATA_DIR/
docker cp data/flavors.csv $CONTAINER_NAME:$CONTAINER_DATA_DIR/
docker cp data/ratio.txt $CONTAINER_NAME:$CONTAINER_DATA_DIR/
docker cp data/cephdf.txt $CONTAINER_NAME:$CONTAINER_DATA_DIR/
docker cp data/volumes.json $CONTAINER_NAME:$CONTAINER_DATA_DIR/

# Run placement check if needed
if [ -f "check-placement.sh" ]; then
    echo "Running placement check..."
    ./check-placement.sh
    
    # Copy placement check results to container
    docker cp data/placement_diff.json $CONTAINER_NAME:$CONTAINER_DATA_DIR/
    
    # Copy instance ID check results if they exist
    if [ -f "data/instance_ids_check.json" ]; then
        docker cp data/instance_ids_check.json $CONTAINER_NAME:$CONTAINER_DATA_DIR/
    fi
fi

echo "Data collection and transfer completed successfully"
