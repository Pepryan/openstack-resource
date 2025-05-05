#!/bin/bash
set -e

# Create necessary directories if they don't exist
mkdir -p data
mkdir -p static/results

# Check if users.json exists, if not create a default one
if [ ! -f data/users.json ]; then
    echo "Creating default users.json file..."
    echo '{"admin": "admin"}' > data/users.json
    echo "Default user created: admin/admin - Please change this password!"
fi

# Execute the command provided as arguments (default: python -B app.py)
exec "$@"
