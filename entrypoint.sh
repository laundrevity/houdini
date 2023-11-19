#!/bin/bash

# Exit script on error
set -e

# Define the venv directory
VENV_DIR="/app/venv"

echo "Setting up the virtual environment..."

# Remove existing venv if exists
if [ -d "$VENV_DIR" ]; then
    echo "Removing existing virtual environment..."
    rm -rf "$VENV_DIR"
fi

# Create a new virtual environment
echo "Creating a new virtual environment..."
python -m venv "$VENV_DIR"

# Activate the venv
source "$VENV_DIR/bin/activate"

# Install dependencies
pip install -r /app/requirements.txt

# Execute the passed command
exec "$@"
