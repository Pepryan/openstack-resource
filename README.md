# OpenStack Resource Allocation Web 🚀

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-green?logo=flask)](https://flask.palletsprojects.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![DataTables](https://img.shields.io/badge/DataTables-1.x-orange?logo=jquery)](https://datatables.net/)
[![OpenStack](https://img.shields.io/badge/OpenStack-Cloud-red?logo=openstack)](https://www.openstack.org/)

Welcome to OpenStack Resource Allocation Web - a lightweight, Python-powered solution for efficient OpenStack resource management and monitoring. This web application simplifies complex resource allocation tasks with an intuitive interface, powerful automation features, and real-time data visualization.

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Technology Stack](#️-technology-stack)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
- [Development Guide](#-development-guide)
  - [Setting Up Development Environment](#setting-up-development-environment)
  - [Code Organization](#code-organization)
  - [Adding New Features](#adding-new-features)
  - [UI/UX Customization](#uiux-customization)
  - [Testing](#testing)
- [Deployment](#-deployment)
  - [Production Setup](#production-setup)
  - [Systemd Service](#systemd-service)
  - [Cron Jobs](#cron-jobs)
- [Data Collection](#-data-collection)
  - [OpenStack Data Scripts](#openstack-data-scripts)
  - [Data Files](#data-files)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🌟 Key Features

| Feature | Description |
|---------|-------------|
| 🖥️ Instance Management | Comprehensive instance listing with advanced search, filtering, and migration tools |
| 💽 Volume Management | Volume listing with usage statistics and volume usage prediction calculator |
| 🍦 Flavor Catalog | Detailed listing of available instance flavors with resource specifications |
| 🎯 Resource Allocation | Placement analysis, compute node monitoring, and resource reservation system |
| 🔄 Data Synchronization | Automated data updates every 2 hours via cron jobs |
| 🔍 Advanced Filtering | Powerful search capabilities with regex support and DataTables integration |
| 📤 Data Export | Easy export of instance and allocation data to various formats |
| 🔐 User Authentication | Secure login system with persistent session management |
| 📊 Data Visualization | Visual representation of resource allocation with interactive charts |
| 📱 Responsive Design | Mobile-friendly interface with adaptive layouts |
| 🌙 Dark Mode | Elegant dark theme for reduced eye strain during night operations |

## 🛠️ Technology Stack

- **Frontend**:
  - HTML5, CSS3, JavaScript (ES6+)
  - DataTables.js for interactive tables with advanced features
  - Tailwind CSS for modern, responsive styling
  - Custom CSS for theming and dark mode support
  - Chart.js for interactive data visualization

- **Backend**:
  - Python 3.x
  - Flask web framework for lightweight, efficient serving
  - Flask-Login for secure authentication and session management
  - Pandas for powerful data processing and transformation
  - Matplotlib for server-side chart generation

- **Data Collection**:
  - Bash scripts for OpenStack CLI interaction
  - OpenStack API for resource data retrieval
  - SSH for secure compute node data collection
  - Ceph integration for storage metrics

- **Data Storage**:
  - Lightweight file-based storage (CSV, TXT, JSON)
  - No database required for simplicity and portability

- **Deployment**:
  - Systemd service for application management and auto-restart
  - Cron jobs for automated data collection and synchronization
  - SSH for secure data transfer between collection and web servers

## 🏗 System Architecture

The application follows a modular, layered architecture designed for efficiency and maintainability:

1. **Data Collection Layer**:
   - Bash scripts interact with OpenStack CLI to collect comprehensive resource data
   - SSH connections to compute nodes gather allocation ratios and configuration details
   - Ceph integration provides storage metrics and utilization data

2. **Data Processing Layer**:
   - Python modules process and transform the raw OpenStack data
   - Pandas handles data manipulation, filtering, and preparation
   - Custom utilities for data formatting and conversion

3. **Web Application Layer**:
   - Flask application with blueprint-based modular organization
   - RESTful API endpoints for dynamic data retrieval
   - Authentication and session management for security

4. **Presentation Layer**:
   - Responsive HTML templates with Jinja2 templating
   - JavaScript for interactive features and real-time updates
   - DataTables for advanced table functionality
   - Chart.js for interactive data visualization

### System Flow

1. **Data Collection**: Scheduled execution of `get-data-aio.sh` script collects data from OpenStack environment
2. **Data Verification**: `check-placement.sh` and `check-instance-ids.sh` verify data consistency
3. **Data Transfer**: Collected data is securely transferred to the web server
4. **Application Processing**: Flask application processes and transforms the data
5. **User Interface**: Web interface presents the data with interactive visualizations
6. **User Interaction**: Users can filter, search, and analyze the resource data

```bash
# Cron job configuration example
11 2-23/2 * * * /bin/bash /home/ubuntu/workdir/scripts/openstack-resource/get-data-aio.sh >> /home/ubuntu/workdir/scripts/openstack-resource/get-data-aio.log 2>&1
```

## 📂 Project Structure

```
openstack-resource/
├── app.py                  # Main application entry point
├── config.py               # Application configuration
├── requirements.txt        # Python dependencies
├── get-data-aio.sh         # Main data collection script
├── check-placement.sh      # Placement verification script
├── check-instance-ids.sh   # Instance ID verification script
├── openstack-resource.service  # Systemd service file
├── data/                   # Data directory (created at runtime)
│   ├── aio.csv             # Instance data with project, flavor, and host info
│   ├── allocation.txt      # Resource allocation data from hypervisors
│   ├── cephdf.txt          # Ceph storage metrics and utilization
│   ├── flavors.csv         # Flavor definitions with resource specifications
│   ├── ratio.txt           # CPU/RAM allocation ratios from compute nodes
│   ├── volumes.json        # Volume data with size and attachment info
│   ├── users.json          # User credentials for authentication
│   ├── reserved.json       # Reserved resources data for capacity planning
│   ├── placement_diff.json # Placement allocation verification results
│   └── instance_ids_check.json # Instance ID verification results
├── models/                 # Data models
│   ├── __init__.py         # User model and model imports
│   └── data_host.py        # Host data model for compute resources
├── routes/                 # Route handlers organized by feature
│   ├── __init__.py         # Blueprint registration
│   ├── auth.py             # Authentication routes (login/logout)
│   ├── allocation.py       # Resource allocation routes
│   ├── compute.py          # Compute node management routes
│   ├── flavor.py           # Flavor listing routes
│   ├── instance.py         # Instance management routes
│   └── volume.py           # Volume management routes
├── static/                 # Static assets
│   ├── DataTables/         # DataTables library for interactive tables
│   ├── chartjs/            # Chart.js library for data visualization
│   ├── tailwind.min.css    # Tailwind CSS framework
│   ├── modern-theme.css    # Custom theme styles with dark mode
│   ├── index.css           # Home page styles
│   ├── list-instances.css  # Instance page styles
│   ├── volumes.css         # Volume page styles
│   ├── allocation.css      # Allocation page styles
│   └── results/            # Generated plots and visualization results
├── templates/              # HTML templates with Jinja2
│   ├── allocation.html     # Resource allocation page
│   ├── index.html          # Home page with migration tools
│   ├── list_all_flavors.html  # Flavor catalog page
│   ├── list_all_instances.html  # Instance listing page
│   ├── login.html          # Authentication page
│   ├── navbar.html         # Navigation component
│   └── volumes.html        # Volume management page
└── utils/                  # Utility functions
    ├── __init__.py         # Utility imports
    ├── data_utils.py       # Data processing utilities
    ├── file_utils.py       # File handling utilities
    └── format_utils.py     # Data formatting and conversion utilities
```

## 🚀 Getting Started

### Prerequisites

- Python 3.x (3.8+ recommended)
- pip package manager
- Access to an OpenStack environment with admin privileges (for data collection)
- OpenStack CLI tools installed and configured
- SSH access to compute nodes (for ratio collection)
- Sudo privileges for systemd service setup (production deployment)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/openstack-resource.git
cd openstack-resource
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv-opre
source venv-opre/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

1. Create the required directory structure:
```bash
mkdir -p data static/results
chmod 750 data  # Secure the data directory
```

2. Create a users.json file for authentication:
```bash
cat > data/users.json << EOF
{
  "admin": "your-secure-password",
  "user1": "another-password"
}
EOF
chmod 640 data/users.json  # Restrict access to the credentials file
```

3. Configure application settings in config.py:
```python
# Security settings
SECRET_KEY = 'your-secure-secret-key'  # Change this to a random secure string
DEBUG = False  # Set to True for development
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 5005  # Application port

# Session configuration
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME_DAYS = 30  # Adjust session duration as needed

# Constants
CORE_COMPUTE = 48  # Number of cores per compute node (adjust to match your environment)
CEPH_ERASURE_CODE = 1.5  # Adjust based on your Ceph configuration
CEPH_TOTAL_SIZE_TB = 6246.4  # Update with your Ceph total size
```

4. Set up OpenStack credentials for data collection:
```bash
# Create or ensure you have a valid OpenStack RC file
cat > ~/admin-openrc << EOF
#!/bin/bash
export OS_AUTH_URL=https://your-openstack-auth-url:5000/v3
export OS_PROJECT_NAME="admin"
export OS_USER_DOMAIN_NAME="Default"
export OS_PROJECT_DOMAIN_NAME="Default"
export OS_USERNAME="admin"
export OS_PASSWORD="your-openstack-admin-password"
export OS_REGION_NAME="RegionOne"
export OS_INTERFACE=public
export OS_IDENTITY_API_VERSION=3
EOF

chmod 600 ~/admin-openrc  # Secure the credentials file
```

5. Modify the data collection script to match your environment:
```bash
# Edit get-data-aio.sh and update the instance_server variable
vim get-data-aio.sh
# Change: instance_server="172.18.218.129:~/openstack-resource/data"
# To match your web server's IP and path
```

### Running the Application

#### Development Mode
```bash
# Start the application in development mode
source venv-opre/bin/activate
python app.py
```
Access the application at `http://localhost:5005`

#### Production Mode
```bash
# Copy the systemd service file
sudo cp openstack-resource.service /etc/systemd/system/

# Edit the service file to match your installation path
sudo vim /etc/systemd/system/openstack-resource.service

# Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable openstack-resource
sudo systemctl start openstack-resource
```

Access the application at `http://your-server-ip:5005`

## 💻 Development Guide

### Setting Up Development Environment

1. Fork and clone the repository
2. Set up virtual environment and install dependencies
3. Enable debug mode in config.py:
   ```python
   DEBUG = True
   ```
4. Create sample data files for testing:
   ```bash
   # Create sample data files with realistic structure
   mkdir -p data static/results

   # Create sample instance data
   cat > data/aio.csv << EOF
   Project|ID|Name|Status|Power State|Networks|Image Name|Image ID|Flavor Name|Flavor ID|Host|CPU|RAM
   admin|12345|test-instance|ACTIVE|Running|net=192.168.1.100|Ubuntu 20.04|abcdef|m1.medium|98765|compute-01|2|4G
   EOF

   # Create sample allocation data
   echo "1 compute-01 enabled up 15 10 20480 10240" > data/allocation.txt

   # Create sample flavor data
   cat > data/flavors.csv << EOF
   ID|Name|RAM|Disk|Ephemeral|VCPUs|Is Public|Swap|RXTX Factor|Properties
   98765|m1.medium|4096|40|0|2|True|0|1.0|hw_rng:allowed=True
   EOF

   # Create sample ratio data
   echo "compute-01, 4, 1.5" > data/ratio.txt

   # Create sample Ceph data
   cat > data/cephdf.txt << EOF
   --- RAW STORAGE ---
   CLASS  SIZE    AVAIL   USED    RAW USED  %RAW USED
   TOTAL  6246G   4500G   1746G   1746G     27.95
   EOF

   # Create sample volume data
   echo '[{"ID":"vol-123","Name":"test-volume","Status":"in-use","Size":10,"Bootable":"true"}]' > data/volumes.json

   # Create sample user data
   echo '{"admin":"password"}' > data/users.json

   # Create sample reserved data
   echo '{"compute-01":{"CPU":"2","RAM":"4096","Kebutuhan":"Reserved for maintenance"}}' > data/reserved.json
   ```

### Code Organization

The application follows a modular blueprint-based structure:

- **Models**: Data structures and user authentication
  - `models/data_host.py`: Compute host data model
  - `models/__init__.py`: User model and authentication

- **Routes**: HTTP route handlers organized by feature
  - `routes/auth.py`: Authentication routes
  - `routes/compute.py`: Compute node management
  - `routes/instance.py`: Instance listing and management
  - `routes/volume.py`: Volume management
  - `routes/allocation.py`: Resource allocation
  - `routes/flavor.py`: Flavor catalog

- **Templates**: HTML templates with Jinja2 templating
  - Layout templates (navbar.html)
  - Feature-specific templates

- **Static**: CSS, JavaScript, and other static assets
  - Third-party libraries (DataTables, Chart.js)
  - Custom CSS for theming and responsive design

- **Utils**: Utility functions for data processing
  - `utils/data_utils.py`: Data processing functions
  - `utils/file_utils.py`: File operations
  - `utils/format_utils.py`: Data formatting

### Adding New Features

1. Create a new blueprint in routes/__init__.py:
   ```python
   new_feature_bp = Blueprint('new_feature', __name__)
   blueprints.append(new_feature_bp)
   ```

2. Create a new route file in the routes/ directory:
   ```python
   # routes/new_feature.py
   from flask import render_template, request, jsonify
   from flask_login import login_required
   from routes import new_feature_bp
   import config

   @new_feature_bp.route('/')
   @login_required
   def index():
       """New feature main page"""
       return render_template('new_feature.html')

   @new_feature_bp.route('/api/data')
   @login_required
   def get_data():
       """API endpoint for new feature data"""
       # Process and return data
       return jsonify({"data": "example"})
   ```

3. Create a template in templates/ directory:
   ```html
   <!-- templates/new_feature.html -->
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>New Feature</title>
       <link rel="stylesheet" href="static/tailwind.min.css">
       <link rel="stylesheet" href="static/modern-theme.css">
       <link rel="stylesheet" href="static/new-feature.css">
   </head>
   <body>
       {% include 'navbar.html' %}
       <div class="main-content">
           <main class="mx-4 mt-8">
               <h1 class="text-2xl font-bold mb-4">New Feature</h1>
               <!-- Feature content here -->
           </main>
       </div>
       <script src="static/new-feature.js"></script>
   </body>
   </html>
   ```

4. Update the navigation in templates/navbar.html:
   ```html
   <!-- Add to the navigation links -->
   <a href="/new-feature" class="nav-link">New Feature</a>
   ```

5. Create CSS and JS files if needed:
   ```bash
   touch static/new-feature.css static/new-feature.js
   ```

### UI/UX Customization

The application uses a combination of Tailwind CSS and custom CSS for styling:

- **modern-theme.css**: Main theme styles and dark mode support
- **Page-specific CSS**: Individual styling for each page

To modify the theme:

1. Global theme changes:
   ```css
   /* static/modern-theme.css */
   :root {
     --primary-color: #3b82f6;  /* Change primary color */
     --secondary-color: #10b981;  /* Change secondary color */
     /* Other theme variables */
   }
   ```

2. Page-specific styling:
   ```css
   /* static/new-feature.css */
   .feature-card {
     border-radius: 0.5rem;
     box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
     /* Other styles */
   }
   ```

3. Dark mode customization:
   ```css
   /* static/modern-theme.css */
   [data-theme="dark"] {
     --bg-color: #121212;
     --text-color: #f3f4f6;
     /* Other dark theme variables */
   }
   ```

### Testing

Manual testing should be performed for all components:

1. Data collection scripts:
   ```bash
   # Test data collection with debug output
   bash -x ./get-data-aio.sh
   ```

2. Data processing functions:
   ```python
   # Add debug prints to verify data processing
   print(f"Processing data: {data}")
   ```

3. UI testing across browsers and devices:
   - Test on Chrome, Firefox, and Safari
   - Test on desktop and mobile devices
   - Verify responsive design at different screen sizes

4. Authentication and session testing:
   - Verify login persistence with "Remember me" option
   - Test session timeout behavior
   - Verify secure access to protected routes

## 🚢 Deployment

### Production Setup

1. Clone the repository on your production server:
   ```bash
   git clone https://github.com/yourusername/openstack-resource.git /home/ubuntu/openstack-resource
   cd /home/ubuntu/openstack-resource
   ```

2. Set up a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv-opre
   source venv-opre/bin/activate
   pip install -r requirements.txt
   ```

3. Configure the application for production:
   ```bash
   # Edit config.py for production settings
   vim config.py
   ```

   Key production settings:
   ```python
   # Use a fixed secret key for session persistence
   SECRET_KEY = 'your-fixed-production-secret-key'  # Change this!
   DEBUG = False
   HOST = "0.0.0.0"
   PORT = 5005

   # Ensure session settings are configured
   SESSION_PERMANENT = True
   PERMANENT_SESSION_LIFETIME_DAYS = 30
   ```

4. Create and secure the data directory:
   ```bash
   mkdir -p data static/results
   chmod 750 data
   ```

5. Set up user authentication:
   ```bash
   # Create users.json with secure passwords
   vim data/users.json
   # Add user credentials in JSON format
   chmod 640 data/users.json
   ```

### Systemd Service

Create a systemd service for automatic startup and management:

1. Create the service file:
   ```bash
   sudo vim /etc/systemd/system/openstack-resource.service
   ```

2. Add the following configuration:
   ```ini
   [Unit]
   Description=OpenStack Resource Allocation Web Application
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   Group=ubuntu
   WorkingDirectory=/home/ubuntu/openstack-resource/
   ExecStart=/home/ubuntu/openstack-resource/venv-opre/bin/python3 -B /home/ubuntu/openstack-resource/app.py
   Restart=on-failure
   RestartSec=5
   StandardOutput=journal
   StandardError=journal
   SyslogIdentifier=openstack-resource
   Environment="PYTHONUNBUFFERED=1"

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable openstack-resource
   sudo systemctl start openstack-resource
   ```

4. Verify the service is running:
   ```bash
   sudo systemctl status openstack-resource
   ```

5. Check the logs if needed:
   ```bash
   sudo journalctl -u openstack-resource -f
   ```

### Cron Jobs

Set up cron jobs for automated data collection:

1. Edit the crontab for the user with OpenStack access:
   ```bash
   crontab -e
   ```

2. Add the following line to run every 2 hours:
   ```bash
   # Run data collection every 2 hours (at 11 minutes past the hour)
   11 */2 * * * /bin/bash /home/ubuntu/workdir/scripts/openstack-resource/get-data-aio.sh >> /home/ubuntu/workdir/scripts/openstack-resource/get-data-aio.log 2>&1
   ```

3. Verify the cron job is scheduled:
   ```bash
   crontab -l
   ```

4. Check the log file after the first scheduled run:
   ```bash
   tail -f /home/ubuntu/workdir/scripts/openstack-resource/get-data-aio.log
   ```

### Nginx Reverse Proxy (Optional)

For production environments, it's recommended to use Nginx as a reverse proxy:

1. Install Nginx:
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. Create a site configuration:
   ```bash
   sudo vim /etc/nginx/sites-available/openstack-resource
   ```

3. Add the following configuration:
   ```nginx
   server {
       listen 80;
       server_name your-server-domain.com;  # Change to your domain or IP

       location / {
           proxy_pass http://127.0.0.1:5005;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. Enable the site and restart Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/openstack-resource /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. Access the application at `http://your-server-domain.com`

## 📊 Data Collection

### OpenStack Data Scripts

The application includes several scripts for collecting and verifying data from OpenStack:

- **get-data-aio.sh**: Main data collection script that gathers instance, flavor, allocation, and volume data
- **check-placement.sh**: Verifies placement allocations to detect inconsistencies between Nova and Placement API
- **check-instance-ids.sh**: Verifies instance IDs when placement inconsistencies are found

#### get-data-aio.sh

This is the primary data collection script that:

1. Sources OpenStack credentials from `~/admin-openrc`
2. Collects instance data for all projects using `openstack server list`
3. Retrieves flavor information with `openstack flavor list`
4. Gathers hypervisor allocation data with `openstack hypervisor list`
5. Collects CPU and RAM allocation ratios from compute nodes via SSH
6. Retrieves Ceph storage metrics with `ceph df`
7. Collects volume data with `openstack volume list`
8. Transfers all collected data to the web server
9. Triggers placement verification with `check-placement.sh`
10. Restarts the web application service

```bash
# Key sections of get-data-aio.sh

# Collect instance data for all projects
for project_name in "${project_names[@]}"; do
    openstack server list --project "$project_name" --limit -1 --long -c ID -c Name -c Status -c "Power State" -c Networks -c "Flavor ID" -c "Flavor Name" -c "Image ID" -c "Image Name" -c Host -f csv | grep -v "ERROR" | sed 's/^"\(.*\)"$/\1/' > temp_aio_project.csv
    # Process and append to main file
    awk -v project="$project_name" -F "|" 'BEGIN {OFS="|"} {print project, $0}' temp_aio_project.csv >> "$output_file"
done

# Collect allocation ratios from compute nodes
for host in $(cat "$file_hosts"); do
    ssh_result=$(ssh "$host" "sudo cat /etc/nova/nova.conf")
    cpu_ratio=$(echo "$ssh_result" | grep -oP "cpu_allocation_ratio = \K\d+(\.\d+)?")
    ram_ratio=$(echo "$ssh_result" | grep -oP "ram_allocation_ratio = \K\d+(\.\d+)?")
    echo "$host, $cpu_ratio, $ram_ratio"
done > ratio.txt
```

#### check-placement.sh

This script verifies the consistency between Nova and Placement API:

1. Gets an authentication token from OpenStack
2. Retrieves resource provider information from Placement API
3. Compares allocation data between Nova and Placement
4. Identifies discrepancies and saves them to `placement_diff.json`
5. Triggers `check-instance-ids.sh` if discrepancies are found

### Data Files

The application uses several data files, each with a specific purpose:

| File | Description | Format | Example Content |
|------|-------------|--------|----------------|
| aio.csv | Instance data with project, flavor, and host information | CSV with pipe delimiter | `Project\|ID\|Name\|Status\|Power State\|Networks\|Image Name\|Image ID\|Flavor Name\|Flavor ID\|Host\|CPU\|RAM` |
| allocation.txt | Resource allocation data from hypervisors | Text file | `1 compute-01 enabled up 15 10 20480 10240` |
| cephdf.txt | Ceph storage metrics and utilization | Text file | `TOTAL 6246G 4500G 1746G 1746G 27.95` |
| flavors.csv | Flavor definitions with resource specifications | CSV with pipe delimiter | `ID\|Name\|RAM\|Disk\|Ephemeral\|VCPUs\|Is Public\|Swap\|RXTX Factor\|Properties` |
| ratio.txt | CPU/RAM allocation ratios from compute nodes | Text file | `compute-01, 4, 1.5` |
| volumes.json | Volume data with size and attachment info | JSON | `[{"ID":"vol-123","Name":"test-volume","Status":"in-use","Size":10}]` |
| users.json | User credentials for authentication | JSON | `{"admin":"password"}` |
| reserved.json | Reserved resources data for capacity planning | JSON | `{"compute-01":{"CPU":"2","RAM":"4096"}}` |
| placement_diff.json | Placement allocation verification results | JSON | `[{"hostname":"compute-01","differences":[...]}]` |
| instance_ids_check.json | Instance ID verification results | JSON | `[{"instance_id":"12345","status":"found"}]` |

### Data Collection Requirements

1. **OpenStack CLI Access**:
   - OpenStack CLI tools installed (`python-openstackclient`)
   - Admin credentials with access to all projects
   - Valid `admin-openrc` file with authentication details

2. **SSH Access**:
   - SSH key-based authentication to compute nodes
   - Sudo access on compute nodes to read Nova configuration

3. **Ceph Access** (if using Ceph storage):
   - Access to Ceph CLI tools
   - Proper Ceph authentication configured

4. **Network Connectivity**:
   - Network access between collection server and web server
   - SSH access for secure file transfer

## 🔧 Troubleshooting

### Common Issues

1. **Data Collection Issues**

   - **OpenStack Authentication Failures**:
     ```bash
     # Check if OpenStack credentials are valid
     source ~/admin-openrc
     openstack token issue

     # Verify OpenStack endpoints
     openstack endpoint list
     ```

   - **SSH Access Problems**:
     ```bash
     # Test SSH access to compute nodes
     ssh compute-node-hostname "hostname"

     # Check SSH key permissions
     ls -la ~/.ssh/
     chmod 600 ~/.ssh/id_rsa
     ```

   - **Ceph Access Issues**:
     ```bash
     # Test Ceph access
     ceph status
     ceph df
     ```

   - **Data Transfer Failures**:
     ```bash
     # Test SCP connection
     touch test_file
     scp test_file ubuntu@web-server-ip:~/
     ```

2. **Application Startup Problems**

   - **Missing Dependencies**:
     ```bash
     # Verify Python dependencies
     source venv-opre/bin/activate
     pip list | grep -E "flask|pandas|matplotlib"

     # Install missing dependencies
     pip install -r requirements.txt
     ```

   - **Permission Issues**:
     ```bash
     # Check data directory permissions
     ls -la data/

     # Fix permissions if needed
     chmod 750 data/
     chmod 640 data/users.json
     ```

   - **Service Configuration**:
     ```bash
     # Check service status
     sudo systemctl status openstack-resource

     # View service logs
     sudo journalctl -u openstack-resource -n 100

     # Restart service
     sudo systemctl restart openstack-resource
     ```

3. **UI and Rendering Issues**

   - **Browser Cache Problems**:
     - Clear browser cache (Ctrl+F5 or Cmd+Shift+R)
     - Try a different browser to isolate the issue
     - Check browser console for JavaScript errors (F12)

   - **CSS Loading Issues**:
     ```bash
     # Check if CSS files exist
     ls -la static/*.css

     # Verify file permissions
     chmod 644 static/*.css
     ```

   - **DataTables Initialization**:
     - Check browser console for DataTables errors
     - Verify DataTables library is properly loaded
     - Check column definitions in JavaScript

4. **Authentication and Session Problems**

   - **Login Failures**:
     ```bash
     # Verify users.json format
     cat data/users.json

     # Ensure it's valid JSON
     python -c "import json; json.load(open('data/users.json'))"
     ```

   - **Session Expiration Issues**:
     - Check `config.py` for session settings
     - Verify `SECRET_KEY` is consistent (not randomly generated on restart)
     - Check browser cookie settings

   - **Remember Me Not Working**:
     - Verify Flask-Login configuration in `app.py`
     - Check `REMEMBER_COOKIE_DURATION` setting
     - Ensure cookies are not being blocked by browser

### Specific Error Messages

- **"No module named 'flask'"**:
  ```bash
  source venv-opre/bin/activate
  pip install flask
  ```

- **"Permission denied" when accessing data files**:
  ```bash
  # Fix ownership and permissions
  sudo chown -R ubuntu:ubuntu /home/ubuntu/openstack-resource/
  chmod -R 750 /home/ubuntu/openstack-resource/
  chmod 640 data/users.json
  ```

- **"Connection refused" when accessing the web interface**:
  ```bash
  # Check if application is running
  ps aux | grep app.py

  # Check firewall settings
  sudo ufw status

  # Allow port if needed
  sudo ufw allow 5005/tcp
  ```

## 🤝 Contributing

Contributions to improve the OpenStack Resource Allocation Web application are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and commit them: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Create a Pull Request

### Contribution Guidelines

- **Code Style**: Follow PEP 8 for Python code
- **Documentation**: Add docstrings to functions and classes
- **Commit Messages**: Write clear, concise commit messages
- **Testing**: Test your changes thoroughly before submitting
- **Branch Naming**: Use descriptive branch names (feature/, bugfix/, etc.)

### Development Workflow

1. **Pick an Issue**: Start with existing issues or create a new one
2. **Discuss**: For major changes, open an issue for discussion first
3. **Develop**: Make your changes in a feature branch
4. **Test**: Ensure your changes work as expected
5. **Submit**: Create a pull request with a clear description

### Coding Standards

- **Python Code**:
  - Follow PEP 8 style guide
  - Use meaningful variable and function names
  - Add docstrings to all functions and classes
  - Keep functions small and focused on a single task

- **JavaScript Code**:
  - Follow ES6 standards where possible
  - Use camelCase for variable and function names
  - Add comments for complex logic

- **HTML/CSS**:
  - Use consistent indentation (2 or 4 spaces)
  - Follow BEM naming convention for CSS classes
  - Keep CSS organized by component

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👏 Acknowledgements

- [OpenStack](https://www.openstack.org/) for the cloud infrastructure platform
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [DataTables](https://datatables.net/) for the interactive table functionality
- [Chart.js](https://www.chartjs.org/) for data visualization
- [Tailwind CSS](https://tailwindcss.com/) for the styling framework