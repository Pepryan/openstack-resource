# OpenStack Resource Allocation Web 🚀

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-green?logo=flask)](https://flask.palletsprojects.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

Welcome to OpenStack Resource Allocation Web - your lightweight, Python-powered solution for efficient OpenStack resource management! This web application simplifies complex resource allocation tasks with an intuitive interface and powerful automation features.

## 🌟 Key Features

| Feature | Description |
|---------|-------------|
| 🖥️ Instance Management | Comprehensive instance listing with advanced search and migration tools |
| 💽 Volume Management | Volume listing with usage statistics and prediction calculator |
| 🍦 Flavor Catalog | Detailed listing of available instance flavors |
| 🎯 Resource Allocation | Placement analysis and resource reservation system |
| 🔄 Data Synchronization | Automated data updates every 2 hours |
| 🔍 Advanced Filtering | Powerful search capabilities with regex support |
| 📤 Data Export | Easy export of instance and allocation data |

## 🛠️ Technology Stack

- **Frontend**: JavaScript, HTML, CSS, DataTables.js
- **Backend**: Python, Flask
- **Data Visualization**: Matplotlib
- **Data Storage**: Lightweight file-based storage (txt, csv, json)

## ⚙️ System Flow

1. Data collection via `get-data-aio.sh` script
2. Automated data synchronization every 2 hours (cron job)
3. Data processing and visualization
4. Web interface for resource management

```bash
# Cron job configuration
11 2-23/2 * * * /bin/bash /home/ubuntu/workdir/scripts/openstack-resource/get-data-aio.sh >> /home/ubuntu/workdir/scripts/openstack-resource/get-data-aio.log 2>&1
```

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/openstack-resource.git
cd openstack-resource
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install matplotlib
```

### Running the Application
```bash
python app.py
```
Access the application at `http://localhost:[port]`

![Screenshot Openstack Resource](/screenshot-opre.png?raw=true "Openstack Resource")

## 🤝 Contributing
While this is primarily a personal project, contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.