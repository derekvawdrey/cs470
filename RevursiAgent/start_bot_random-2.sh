#!/bin/bash
# Source the virtual environment
source /Users/derekvawdrey/Workspace/school/cs270/venv/bin/activate


# Start both Python clients with daemon flag
python cs-470-reversi-python-client/reversi_python_client.py localhost 2 1 0 0 0 0 0 1

# Deactivate the virtual environment
deactivate 