# Openstack Resource Allocation Web


### Feature
- Info vCPUs compute
- List instance on compute with vCPU
- Move instance
- Generate plot vCPUs allocation (work on progress, you can still see the generated image on your project directory)

### Tech used
- Vanilla javascript, HTML, CSS
- python
- flask

### Still on check (known bugs)
- Data aio.csv not update (not yet updated as of Sept 2023)
- Data from allocation.txt and sum of vCPUs not same (because aio.csv not update)
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