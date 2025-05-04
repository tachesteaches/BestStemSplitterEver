#!/bin/bash
echo "Fixing permissions for BestStemSplitterEver scripts..."

# Make all shell scripts executable
chmod +x run.sh
chmod +x setup.sh
chmod +x drumsep/drumsep
chmod +x drumsep/drumsep.py
chmod +x drumsep/drumsepInstall
chmod +x fix_permissions.sh

echo "✅ Permissions fixed!"