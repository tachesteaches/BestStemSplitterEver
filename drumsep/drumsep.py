#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def separate_drums(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(exist_ok=True)
    
    # Get the location of the script and model
    script_dir = Path(__file__).parent.absolute()
    model_dir = script_dir / "model"
    
    if input_path.is_dir():
        # Process all audio files in directory
        audio_extensions = [".mp3", ".wav", ".ogg", ".flac"]
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(list(input_path.glob(f"*{ext}")))
        
        for audio_file in audio_files:
            run_demucs(audio_file, output_path, model_dir)
    else:
        # Process single file
        run_demucs(input_path, output_path, model_dir)
    
    return True

def run_demucs(audio_file, output_path, model_dir):
    print(f"Processing {audio_file}...")
    
    # Run demucs with the drum model
    subprocess.run([
        "demucs", 
        "--repo", str(model_dir),
        "-o", str(output_path),
        "-n", "49469ca8", 
        str(audio_file)
    ])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python drumsep.py <input_path> <output_path>")
        sys.exit(1)
    
    success = separate_drums(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)