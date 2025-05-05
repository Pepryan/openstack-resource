# Docker Deployment for Aether

This guide explains how to deploy Aether using Docker for easier deployment and environment consistency.

## 🐳 Docker Installation

### Prerequisites

- Docker Engine installed on your server
- Docker Compose installed on your server
- Access to an OpenStack environment with admin privileges (for data collection)

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Pepryan/openstack-resource.git aether
cd aether
```

2. Build and start the Docker container:
```bash
docker-compose up -d
```

3. Access the application at `http://your-server-ip:5005`

### Docker Configuration

The Docker setup includes:

- **Dockerfile**: Defines the container image with all dependencies
- **docker-compose.yml**: Configures the application service with volumes and networking
- **docker-entrypoint.sh**: Initializes the container environment
- **docker-data-collector.sh**: Collects data from OpenStack and transfers it to the container

## 🔄 Data Collection with Docker

When using Docker, the data collection process is slightly different:

1. On your OpenStack server, run the data collection script:
```bash
# Make the script executable
chmod +x docker-data-collector.sh

# Run the script
./docker-data-collector.sh
```

2. The script will:
   - Collect data from OpenStack using the standard collection scripts
   - Transfer the data directly to the Docker container
   - No need to manually restart the application

## 🛠️ Docker Management

### Viewing Logs

```bash
# View application logs
docker logs openstack-resource

# Follow logs in real-time
docker logs -f openstack-resource
```

### Restarting the Application

```bash
# Restart the container
docker-compose restart
```

### Updating the Application

```bash
# Pull the latest changes
git pull

# Rebuild and restart the container
docker-compose up -d --build
```

## 📂 Docker Volumes

The Docker setup uses volumes to persist data:

- **./data:/app/data**: Stores all data files
- **./static/results:/app/static/results**: Stores generated charts and visualizations

## 🔧 Troubleshooting Docker Deployment

### Container Won't Start

Check the Docker logs:
```bash
docker logs openstack-resource
```

Verify the volumes are properly mounted:
```bash
docker inspect openstack-resource
```

### Data Collection Issues

If the data collection script fails:

1. Check if the container is running:
```bash
docker ps | grep openstack-resource
```

2. Verify the container name in the script matches your actual container name

3. Try running the data collection manually:
```bash
# Copy a file directly to the container
docker cp data/aio.csv openstack-resource:/app/data/
```

### Permission Issues

If you encounter permission issues:

```bash
# Fix permissions on the host
chmod -R 755 data
chmod -R 755 static/results

# Restart the container
docker-compose restart
```
