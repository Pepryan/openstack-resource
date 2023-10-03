# Openstack Resource Allocation Web
Welcome to OpenStack Resource Allocation Web, a lightweight and minimal Python-based web application that simplifies OpenStack resource allocation information. With just a few easy clicks, you can swiftly do a simulation move instances to meet your needs.

### Flow
- Script `get-data-aio.sh` collect data from controller > scp the data files to instance reporting
- Data will be updated every 2 hours, on crontab ubuntu controller-1, sync with `get-data-aio.sh` script
```bash
11 2-23/2 * * * /bin/bash /home/ubuntu/workdir/scripts/openstack-resource/get-data-aio.sh >> /home/ubuntu/workdir/scripts/openstack-resource/get-data-aio.log 2>&1
```

### Feature
- Info vCPUs compute
- List instance on compute with vCPU
- Generate plot vCPUs allocation
- Data will be automated sync with script
- List all instance with necessary metadata, filtering feature, exporting feature
- and many more

### Tech used
- Javascript, HTML, CSS
- python
- flask
- matplotlib
- No Database required (just use txt, csv and json for storing data)

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
pip install matplotlib
```

##### Run app
```bash
python app.py
open browser localhost:[port]
```