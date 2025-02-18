#!/bin/bash
# Source the virtual environment
source /Users/derekvawdrey/Workspace/school/cs270/venv/bin/activate

# Start both Python clients with daemon flag
python reversi-client-genetic/reversi_python_client.py localhost 1 7 0.234 0.5999 0 0.405 0.777 0 0
# Deactivate the virtual environment
deactivate 