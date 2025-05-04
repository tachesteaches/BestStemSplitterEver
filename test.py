#!/usr/bin/env python3
import os
import sys
import platform
import importlib.util

def check_module(name):
    """Check if a module can be imported."""
    try:
        importlib.import_module(name)
        return True
    except ImportError:
        return False

def check_file(path):
    """Check if a file exists."""
    return os.path.isfile(path)

def check_dir(path):
    """Check if a directory exists."""
    return os.path.isdir(path)

def print_status(message, success):
    """Print a status message with color."""
    if success:
        prefix = "✅"
    else:
        prefix = "❌"
    print(f"{prefix} {message}")
    return success

def main():
    all_good = True
    
    # Check Python version
    python_version = sys.version_info
    all_good &= print_status(
        f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}",
        python_version.major >= 3 and python_version.minor >= 8
    )
    
    # Check critical dependencies
    for module in ["librosa", "numpy", "yaml", "demucs"]:
        all_good &= print_status(f"Module {module}", check_module(module))
    
    # Check directory structure
    for directory in ["drumsep", "drumsep/model"]:
        all_good &= print_status(f"Directory {directory}", check_dir(directory))
    
    # Check critical files
    for file_path in ["stem_splitter.py", "config.yaml", "requirements.txt"]:
        all_good &= print_status(f"File {file_path}", check_file(file_path))
    
    # Check drumsep files
    if platform.system() == "Windows":
        all_good &= print_status("drumsep.py script", check_file("drumsep/drumsep.py"))
    else:
        all_good &= print_status("drumsep script", check_file("drumsep/drumsep") and os.access("drumsep/drumsep", os.X_OK))
        all_good &= print_status("drumsep.py script", check_file("drumsep/drumsep.py") and os.access("drumsep/drumsep.py", os.X_OK))
    
    # Final verdict
    if all_good:
        print("\n✅ All checks passed! Your setup appears to be working correctly.")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues above before sharing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())