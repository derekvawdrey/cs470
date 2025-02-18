#!/bin/bash
# Source the virtual environment
source /Users/derekvawdrey/Workspace/school/cs270/venv/bin/activate

# Start both Python clients with daemon flag
python reversi-client-genetic/reversi_python_client.py localhost 1 5 -0.895 0.491 0.767 -0.325 0.392 0.162 0.230

# Deactivate the virtual environment
deactivate 