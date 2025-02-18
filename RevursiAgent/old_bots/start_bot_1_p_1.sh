#!/bin/bash
# Source the virtual environment
source /Users/derekvawdrey/Workspace/school/cs270/venv/bin/activate

# Start both Python clients with daemon flag
python reversi-client-genetic/reversi_python_client.py localhost 1 2 -1.03 0.662 0.767 -0.325 0.392 0.173 -0.631

# Deactivate the virtual environment
deactivate 