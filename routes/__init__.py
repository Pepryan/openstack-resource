from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__)
compute_bp = Blueprint('compute', __name__)
instance_bp = Blueprint('instance', __name__)
volume_bp = Blueprint('volume', __name__)
allocation_bp = Blueprint('allocation', __name__)
flavor_bp = Blueprint('flavor', __name__)
ai_chat_bp = Blueprint('ai_chat', __name__)

# Import routes
from routes.auth import *
from routes.compute import *
from routes.instance import *
from routes.volume import *
from routes.allocation import *
from routes.flavor import *
from routes.ai_chat import *

# List of all blueprints
blueprints = [
    auth_bp,
    compute_bp,
    instance_bp,
    volume_bp,
    allocation_bp,
    flavor_bp,
    ai_chat_bp
]
