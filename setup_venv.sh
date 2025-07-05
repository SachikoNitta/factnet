#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

echo "Virtual environment setup complete!"
echo "To activate: source venv/bin/activate"
echo "To run example: python example.py"