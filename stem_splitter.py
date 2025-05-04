#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import time
import re
from pathlib import Path
import glob
import yaml
import argparse
import platform  # NEW: For platform detection

# Try to import librosa, but provide helpful message if not installed
try:
    import librosa
except ImportError:
    print("Error: librosa is not installed.")
    print("Please install it using: pip install librosa")
    print("See requirements.txt for all dependencies.")
    sys.exit(1)

def load_config(config_path=None):
    """Load configuration from YAML file or use defaults."""
    # Default config path is in the same directory as the script
    if config_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config.yaml")
    
    # Default configuration
    default_config = {
        "paths": {
            "temp_dir": "~/BestStemSplitterEver/temp",
            "output_dir": "~/Music/Stems"
        },
        "tools": {
            "drumsep_dir": "./drumsep",  # CHANGED: Use relative path
            "demucs_model": "htdemucs_6s"
        },
        "output": {
            "organize_by_song": True,
            "include_key_bpm": True,
            "filename_format": "{key} - {bpm}BPM - {name} - ({stem})"
        }
    }
    
    # Load from file if it exists
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as config_file:
                config = yaml.safe_load(config_file)
                print(f"✅ Loaded configuration from {config_path}")
        except Exception as e:
            print(f"⚠️ Error loading config file: {e}")
            print("Using default configuration.")
            config = default_config
    else:
        print(f"⚠️ Config file not found at {config_path}")
        print("Using default configuration.")
        config = default_config
        
        # Write default config for user to edit later
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as config_file:
                yaml.dump(default_config, config_file, default_flow_style=False)
            print(f"✅ Created default config at {config_path}")
        except Exception as e:
            print(f"⚠️ Error creating default config: {e}")
    
    # Expand all paths with user home directory
    config["paths"]["temp_dir"] = os.path.expanduser(config["paths"]["temp_dir"])
    config["paths"]["output_dir"] = os.path.expanduser(config["paths"]["output_dir"])
    
    # CHANGED: Only expand drumsep_dir if it's an absolute path
    if config["tools"]["drumsep_dir"].startswith("~"):
        config["tools"]["drumsep_dir"] = os.path.expanduser(config["tools"]["drumsep_dir"])
    else:
        # Convert relative path to absolute
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config["tools"]["drumsep_dir"] = os.path.normpath(os.path.join(script_dir, config["tools"]["drumsep_dir"]))
    
    return config

def get_song_name(file_path):
    """Extract just the filename without extension"""
    return os.path.splitext(os.path.basename(file_path))[0]

def run_command(command, desc):
    """Run a shell command and display its output"""
    print(f"\n🔄 {desc}...\n")
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"⚠️ Command failed with error code {result.returncode}")
        print(f"Error output: {result.stderr}")
        return False
    return True

def detect_key_and_tempo(audio_file):
    """Detect musical key and tempo using librosa"""
    print(f"Analyzing key and tempo for {os.path.basename(audio_file)}...")
    
    # Load the audio file
    y, sr = librosa.load(audio_file)
    
    # Detect tempo
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    # Fix: tempo is a numpy array, need to convert to a scalar
    tempo = round(float(tempo.item() if hasattr(tempo, 'item') else tempo))

    # Analyze the key using chroma features
    chroma = librosa.feature.chroma_cqt(y=librosa.effects.harmonic(y), sr=sr)
    chroma_avg = chroma.mean(axis=1)
    
    # Key detection using correlation with key profiles
    # Major and minor key profiles (Krumhansl-Kessler profiles)
    major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
    minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
    
    key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Calculate correlation for each key
    major_corr = [sum(chroma_avg[i] * major_profile[(i - j) % 12] for i in range(12)) for j in range(12)]
    minor_corr = [sum(chroma_avg[i] * minor_profile[(i - j) % 12] for i in range(12)) for j in range(12)]
    
    # Find the key with the highest correlation
    max_major_idx = major_corr.index(max(major_corr))
    max_minor_idx = minor_corr.index(max(minor_corr))
    
    if max(major_corr) > max(minor_corr):
        key = key_names[max_major_idx]
    else:
        key = f"{key_names[max_minor_idx]}m"
    
    # Get Camelot notation
    camelot_map = {
        'C': '8B', 'G': '9B', 'D': '10B', 'A': '11B', 'E': '12B', 'B': '1B', 
        'F#': '2B', 'C#': '3B', 'G#': '4B', 'D#': '5B', 'A#': '6B', 'F': '7B',
        'Am': '8A', 'Em': '9A', 'Bm': '10A', 'F#m': '11A', 'C#m': '12A', 'G#m': '1A', 
        'D#m': '2A', 'A#m': '3A', 'Fm': '4A', 'Cm': '5A', 'Gm': '6A', 'Dm': '7A'
    }
    
    camelot_key = camelot_map.get(key, "")
    
    return key, camelot_key, tempo

def format_filename(template, data):
    """Format a filename according to the template."""
    return template.format(**data)

# NEW: Cross-platform way to open a folder
def open_folder(folder_path):
    """Open the folder in the system file explorer in a platform-independent way."""
    try:
        if platform.system() == "Windows":
            os.startfile(folder_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", folder_path], check=True)
        else:  # Linux and others
            subprocess.run(["xdg-open", folder_path], check=True)
        print(f"✅ Opened result folder: {folder_path}")
    except Exception as e:
        print(f"⚠️ Could not open folder: {e}")

def run_drumsep(drums_file, output_dir, drumsep_dir):
    """Run drumsep using the Python module instead of bash script."""
    try:
        drumsep_py = os.path.join(drumsep_dir, "drumsep.py")
        
        # If the Python script exists, use it
        if os.path.exists(drumsep_py):
            print(f"Running drumsep.py on {os.path.basename(drums_file)}...")
            
            # Store original sys.path to restore it later
            original_sys_path = sys.path.copy()
            
            # Add drumsep directory to path temporarily
            sys.path.insert(0, drumsep_dir)
            
            try:
                from drumsep import drumsep
                result = drumsep.separate_drums(drums_file, output_dir)
                
                # Restore original sys.path
                sys.path = original_sys_path
                return result
            except ImportError:
                print("⚠️ Could not import drumsep module, falling back to script")
                sys.path = original_sys_path
                # Fall back to script approach
        
        # Fall back to bash script if Python version not found or failed
        drumsep_script = os.path.join(drumsep_dir, "drumsep")
        if not os.path.exists(drumsep_script):
            print(f"⚠️ Drumsep script not found at {drumsep_script}")
            return False
            
        # Use platform-specific approach
        if platform.system() == "Windows":
            # For Windows: Use Python to call the script
            drumsep_cmd = f'python "{drumsep_py}" "{drums_file}" "{output_dir}"'
        else:
            # For Unix-like systems: Use bash
            drumsep_cmd = f'cd "{drumsep_dir}" && bash drumsep "{drums_file}" "{output_dir}"'
            
        return run_command(drumsep_cmd, "Splitting drum stems")
    except Exception as e:
        print(f"⚠️ Error running drumsep: {e}")
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Split audio into stems with key and BPM detection")
    parser.add_argument("input_file", help="Audio file to process")
    parser.add_argument("-c", "--config", help="Path to config file")
    parser.add_argument("-o", "--output", help="Override output directory")
    parser.add_argument("-m", "--model", help="Override demucs model (e.g., htdemucs, htdemucs_6s, mdx_extra)")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override output directory if specified
    if args.output:
        config["paths"]["output_dir"] = os.path.abspath(args.output)
        
    # Override demucs model if specified
    if args.model:
        config["tools"]["demucs_model"] = args.model
        print(f"Overriding demucs model to: {args.model}")
    
    # Ensure directories exist
    os.makedirs(config["paths"]["temp_dir"], exist_ok=True)
    os.makedirs(config["paths"]["output_dir"], exist_ok=True)
    
    # Check that drumsep exists
    drumsep_py = os.path.join(config["tools"]["drumsep_dir"], "drumsep.py")
    drumsep_script = os.path.join(config["tools"]["drumsep_dir"], "drumsep")
    
    if not (os.path.exists(drumsep_py) or os.path.exists(drumsep_script)):
        print(f"⚠️ Drumsep script not found at {drumsep_py} or {drumsep_script}")
        print("Drum separation will be skipped.")
        use_drumsep = False
    else:
        use_drumsep = True
    
    # Get input file and song name
    input_file = os.path.abspath(args.input_file)
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        sys.exit(1)
    
    song_name = get_song_name(input_file)
    
    # Detect key and tempo
    try:
        key, camelot, tempo = detect_key_and_tempo(input_file)
        print(f"Detected key: {key} ({camelot}), tempo: {tempo} BPM")
    except Exception as e:
        print(f"⚠️ Error detecting key and tempo: {e}")
        print("Using default values")
        key, camelot, tempo = "Unknown", "", 0
    
    # Format data for filenames
    file_data = {
        "key": key,
        "camelot": camelot,
        "bpm": tempo,
        "name": song_name,
        "stem": ""  # Will be replaced for each stem
    }
    
    # Create formatted song name
    if config["output"]["include_key_bpm"]:
        formatted_name_base = format_filename(
            config["output"]["filename_format"].replace(" - ({stem})", ""), 
            file_data
        )
    else:
        formatted_name_base = song_name
    
    # Set up output directory
    if config["output"]["organize_by_song"]:
        output_dir = os.path.join(config["paths"]["output_dir"], formatted_name_base)
    else:
        output_dir = config["paths"]["output_dir"]
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the demucs model from config
    demucs_model = config["tools"].get("demucs_model", "htdemucs_6s")
    print(f"Using demucs model: {demucs_model}")
    
    # Run demucs
    demucs_output_dir = os.path.join(config["paths"]["temp_dir"], demucs_model)
    demucs_cmd = f'demucs -n {demucs_model} --out "{config["paths"]["temp_dir"]}" "{input_file}"'
    
    if not run_command(demucs_cmd, "Splitting stems with demucs"):
        print("⚠️ Demucs failed. Aborting.")
        sys.exit(1)
    
    # Find the created demucs folder
    demucs_song_dir = os.path.join(demucs_output_dir, song_name)
    if not os.path.exists(demucs_song_dir):
        print(f"⚠️ Demucs output directory not found at {demucs_song_dir}")
        print("Check if demucs ran successfully.")
        sys.exit(1)
    
    # Determine which stems to look for based on the model
    demucs_model = config["tools"]["demucs_model"]
    
    # Define stems available for each model
    model_stems = {
        "htdemucs": ["bass", "drums", "other", "vocals"],
        "htdemucs_6s": ["bass", "drums", "other", "vocals", "piano", "guitar"],
        "htdemucs_ft": ["bass", "drums", "other", "vocals"],
        "mdx_extra": ["bass", "drums", "other", "vocals"],
        "mdx_extra_q": ["bass", "drums", "other", "vocals"]
    }
    
    # Get stem types for the selected model or use default
    stem_types = model_stems.get(demucs_model, ["bass", "drums", "other", "vocals"])
    print(f"Looking for stems: {', '.join(stem_types)}")
    
    # Rename the stems from demucs
    for stem_type in stem_types:
        source_file = os.path.join(demucs_song_dir, f"{stem_type}.wav")
        if os.path.exists(source_file):
            file_data["stem"] = stem_type.title()
            formatted_name = format_filename(config["output"]["filename_format"], file_data)
            dest_file = os.path.join(output_dir, f"{formatted_name}.wav")
            shutil.copy2(source_file, dest_file)
            print(f"✅ Copied and renamed: {dest_file}")
        else:
            print(f"⚠️ Stem not found: {stem_type}.wav")
    
    # Copy and rename the original file
    file_data["stem"] = "Full Track"
    formatted_name = format_filename(config["output"]["filename_format"], file_data)
    full_track_file = os.path.join(output_dir, f"{formatted_name}.wav")
    shutil.copy2(input_file, full_track_file)
    print(f"✅ Copied original file as: {full_track_file}")
    
    # Run drum separator on the drums stem if available
    # After processing the main stems with demucs, always run drum separation
    file_data["stem"] = "Drums"
    formatted_name = format_filename(config["output"]["filename_format"], file_data)
    drums_file = os.path.join(output_dir, f"{formatted_name}.wav")

    print(f"Running drum separation on {formatted_name}.wav...")

    # Directly call drumsep.py with proper paths
    drumsep_py = os.path.join(config["tools"]["drumsep_dir"], "drumsep.py")
    drumsep_cmd = f'python "{drumsep_py}" "{drums_file}" "{output_dir}"'

    # Run the command
    success = run_command(drumsep_cmd, "Splitting drum stems")

    # Initialize model_id_folder variable
    model_id = "49469ca8"
    model_id_folder = os.path.join(output_dir, model_id)
    
    # Initialize subfolders list
    subfolders = []

    if success:
        print("✅ Drum separation completed successfully")
        
        if os.path.exists(model_id_folder):
            print(f"Found drum separation folder: {model_id_folder}")
            
            # Look for the subfolder with the actual separated drum parts
            subfolders = [d for d in os.listdir(model_id_folder) 
                        if os.path.isdir(os.path.join(model_id_folder, d))]
        else:
            print(f"⚠️ Drumsep output folder not found at: {model_id_folder}")
    
    if subfolders:
        # Rename the files to follow our naming convention
        drum_folder = os.path.join(model_id_folder, subfolders[0])
        
        # Map Spanish names to English
        drum_parts = {
            "bombo.wav": "Kick",
            "platillos.wav": "Hats",
            "redoblante.wav": "Snare-Clap",
            "toms.wav": "Toms"
        }
        
        # Copy and rename files
        for source_name, target_stem in drum_parts.items():
            source_file = os.path.join(drum_folder, source_name)
            if os.path.exists(source_file):
                file_data["stem"] = target_stem
                part_name = format_filename(config["output"]["filename_format"], file_data)
                target_file = os.path.join(output_dir, f"{part_name}.wav")
                shutil.copy2(source_file, target_file)
                print(f"✅ Added drum part: {part_name}.wav")
        
        # Clean up the temporary folder
        shutil.rmtree(model_id_folder)
        print(f"✅ Cleaned up temporary files")
    else:
        print("⚠️ No subfolders found in drumsep output")
    
    # Clean up original demucs output directory
    if os.path.exists(demucs_song_dir):
        shutil.rmtree(demucs_song_dir)
        print(f"✅ Cleaned up demucs output directory: {demucs_song_dir}")
    
    # CHANGED: Use cross-platform folder opening
    open_folder(output_dir)
    
    print(f"\n✨ All done! Your stems are ready in: {output_dir}")

if __name__ == "__main__":
    main()