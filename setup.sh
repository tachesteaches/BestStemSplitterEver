#!/bin/bash
echo "Installing BestStemSplitterEver"
echo "==============================="
python3 setup.py
# Make sure scripts are executable
chmod +x drumsep/drumsep
chmod +x drumsep/drumsep.py
chmod +x run.sh