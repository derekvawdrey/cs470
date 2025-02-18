#!/bin/bash
# Source the virtual environment
source /Users/derekvawdrey/Workspace/school/cs270/venv/bin/activate

# Start both Python clients with daemon flag
python reversi-client-genetic/reversi_python_client.py localhost 2 6 -0.972 -0.958 0.921 0.962 0.931 0.006 0

# Deactivate the virtual environment
deactivate 