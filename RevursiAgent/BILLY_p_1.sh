#!/bin/bash
# Source the virtual environment
source /Users/derekvawdrey/Workspace/school/cs270/venv/bin/activate

# Start both Python clients with daemon flag
python reversi-client-genetic/reversi_python_client.py localhost 1 7 0.977850005799256 0.05603946889909628 0.3298597123660477 0.0738559941747099 0.8596336223609152 0.042110725478221506 0.5927076829716719
# Deactivate the virtual environment
deactivate 