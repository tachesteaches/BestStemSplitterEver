#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
from pathlib import Path

def install_dependencies():
    print("Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("Installing Demucs...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "demucs"])
    
    print("Setting up drum separation model...")
    download_drumsep_model()

def download_drumsep_model():
    drumsep_dir = Path("drumsep")
    model_dir = drumsep_dir / "model"
    
    if not model_dir.exists():
        print("Creating model directory...")
        model_dir.mkdir(exist_ok=True)
        
        # Install gdown if not present
        print("Installing gdown for model download...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])
        
        # Download the model file
        print("Downloading drum separation model (this may take a while)...")
        model_file = model_dir / "49469ca8.th"
        subprocess.check_call([
            sys.executable, "-m", "gdown", 
            "1-Dm666ScPkg8Gt2-lK3Ua0xOudWHZBGC",
            "-O", str(model_file)
        ])
        
        # Create a .gitkeep file to ensure the directory exists but model isn't tracked
        gitkeep_file = model_dir / ".gitkeep"
        with open(gitkeep_file, "w") as f:
            f.write("# This directory contains the downloaded model file\n")
            f.write("# The model file itself is not tracked in git due to size\n")
    
    print("✅ Drum separation model installed")

def main():
    print("=== Setting up BestStemSplitterEver ===")
    install_dependencies()
    print("\n✅ Installation complete!")
    print("\nRun the program with: python stem_splitter.py your_audio_file.mp3")

if __name__ == "__main__":
    main()