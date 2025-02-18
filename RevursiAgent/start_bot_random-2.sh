#!/bin/bash
# Source the virtual environment
source /Users/derekvawdrey/Workspace/school/cs270/venv/bin/activate


# Start both Python clients with daemon flag
python reversi-client-genetic/reversi_python_client.py localhost 2 1 0 0 0 0 0 1 0

# Deactivate the virtual environment
deactivate 