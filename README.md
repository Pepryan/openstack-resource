# Openstack Resource Allocation Web
Welcome to OpenStack Resource Allocation Web, a lightweight and minimal Python-based web application that simplifies OpenStack resource allocation information. With just a few easy clicks, you can swiftly move instances to meet your needs.

### Flow
- Script get-data-aio.sh collect data from controller > scp the data files to instance reporting
- Data will be updated every 2 hours

### Feature
- Info vCPUs compute
- List instance on compute with vCPU
- Move instance
- Generate plot vCPUs allocation (work on progress, you can still see the generated image on your project directory)
- Data will be automated sync with script
- List all instance with image name, flavor name, VCPUs and RAM

### Tech used
- Vanilla javascript, HTML, CSS
- python
- flask

### Still on check (known bugs)
- Picture when "Generate Plot" can be only see in the "Results" project dir, not yet implement in frontend (still error)
- Picture plot allocation only listing instance on destination host (instance to move not yet added)

### Development
Clone this repo to your machine
```bash
git clone (this repo)
cd openstack-resource
```
##### Create virtual environment
```bash 
python3 -m venv venv
source venv/bin/activate
```

##### Install Dependencies
```bash
pip install -r requirements.txt
```

##### Run app
```bash
python app.py
buka browser localhost:5000
```