#!/bin/bash

# Source the virtual environment
source /Users/derekvawdrey/Workspace/school/cs270/venv/bin/activate

# Start the Java server in the background
java -cp ./ReversiServer Reversi 1

# Deactivate the virtual environment
deactivate 