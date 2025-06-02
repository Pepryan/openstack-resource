import os

# Flask configuration
# Using a hardcoded secret key to ensure session persistence
SECRET_KEY = 'febryan-mazfeb-fixed-secret-key-for-sessions-do-not-change'
DEBUG = True
HOST = "0.0.0.0"
PORT = 5005

# Session configuration
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME_DAYS = 30

# File paths
DATA_DIR = 'data'
AIO_CSV_PATH = os.path.join(DATA_DIR, 'aio.csv')
RATIO_FILE_PATH = os.path.join(DATA_DIR, 'ratio.txt')
ALLOCATION_FILE_PATH = os.path.join(DATA_DIR, 'allocation.txt')
USERS_FILE_PATH = os.path.join(DATA_DIR, 'users.json')
VOLUMES_FILE_PATH = os.path.join(DATA_DIR, 'volumes.json')
FLAVORS_FILE_PATH = os.path.join(DATA_DIR, 'flavors.csv')
RESERVED_FILE_PATH = os.path.join(DATA_DIR, 'reserved.json')
CEPHDF_FILE_PATH = os.path.join(DATA_DIR, 'cephdf.txt')
PLACEMENT_DIFF_FILE_PATH = os.path.join(DATA_DIR, 'placement_diff.json')
INSTANCE_IDS_CHECK_FILE_PATH = os.path.join(DATA_DIR, 'instance_ids_check.json')
VOLUME_STATS_FILE_PATH = os.path.join(DATA_DIR, 'volume_stats.json')

# Constants
CSV_DELIMITER = '|'
CORE_COMPUTE = 48  # Number of cores per compute node
CEPH_ERASURE_CODE = 1.5
CEPH_TOTAL_SIZE_TB = 6246.4 #GTI
# ODC 3891.2

# Date format
DATE_FORMAT = '%d-%m-%Y %H:%M:%S'

# AI Model Configuration
AI_MODEL_NAME = 'gemini-2.0-flash'
AI_MODEL_TEMPERATURE = 0.7
AI_MODEL_MAX_TOKENS = 8192
AI_MODEL_TOP_P = 0.9
AI_MODEL_TOP_K = 40
