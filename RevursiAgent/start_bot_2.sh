#!/bin/bash
# Source the virtual environment
source /Users/derekvawdrey/Workspace/school/cs270/venv/bin/activate


# Start both Python clients with daemon flag
python cs-470-reversi-python-client/reversi_python_client.py localhost 2 4 -0.9724278637348411 -0.9575917958507336 0.49051641446111605 -0.11043431912527724 0.9305262003315051 0.005978367003628637 

# Deactivate the virtual environment
deactivate 