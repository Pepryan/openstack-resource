# Openstack Resource Allocation Web
Data is still static from file aio.csv, ratio.txt, and allocation.txt (not sync automatically)

### Feature
- Info vCPUs compute
- List instance on compute with vCPU
- Move instance
- Generate plot vCPUs allocation (work on progress, you can still see the generated image on your project directory)

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