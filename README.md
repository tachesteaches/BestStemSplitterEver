# BestStemSplitterEver

A powerful audio stem splitter that detects key and BPM, separates tracks into stems, and even breaks down drum tracks into individual components.

## Features

- 🎵 Automatically detects musical key and BPM of audio tracks
- 🎚️ Separates audio into multiple stems (vocals, bass, drums, other)
- 🥁 Splits drum stems into individual components (kick, snare, hats, toms)
- 🏷️ Names files with key and BPM information for easy organization
- ⚙️ Configurable output directories and file naming

## Requirements

- Python 3.8 or higher (I'm on Python 3.11.11 and it's working. 3.13 didn't work for a friend)
- Demucs (for stem separation)
- Drumsep (for drum separation)

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/glittercowboy/BestStemSplitterEver.git
   cd BestStemSplitterEver
   ```

2. Run the setup script:

   On Mac / Linux:

   ```
   ./setup.sh
   ```

   or

   On Windows:

   ```
   ./setup.bat
   ```

3. Run the script with:

   On Mac / Linux:

   ```
   ./run.sh {PATH TO YOUR AUDIO FILE - EASY TO JUST DRAG AND DROP IT ONTO TERMINAL}
   ```

   On Windows:

   ```
   run.bat {PATH TO YOUR AUDIO FILE - EASY TO JUST DRAG AND DROP IT ONTO TERMINAL}
   ```

## Cross-Platform Installation

### Windows

1. Install Python 3.8+ from [python.org](https://python.org)
2. Double-click `setup.bat` to install all dependencies
3. Drag and drop any audio file onto `run.bat` to process it

### macOS

1. Make sure Python 3.8+ is installed
2. Open Terminal in the project directory
3. Run: `chmod +x setup.sh run.sh`
4. Run: `./setup.sh`
5. Process an audio file: `./run.sh your_song.mp3`

### Linux

1. Make sure Python 3.8+ is installed
2. Open Terminal in the project directory
3. Run: `chmod +x setup.sh run.sh`
4. Run: `./setup.sh`
5. Process an audio file: `./run.sh your_song.mp3`

### Note for macOS/Linux Users

If you encounter any "Permission denied" errors when running the scripts, you may need to fix the permissions first:

```bash
chmod +x fix_permissions.sh
./fix_permissions.sh
```

## Configuration

Edit the `config.yaml` file to customize your setup:

```yaml
# BestStemSplitterEver Configuration

# Directories
paths:
  # Where temporary demucs files will be stored
  temp_dir: "~/BestStemSplitter/temp"

  # Where final stems will be saved
  output_dir: "~/Music/Stems"

# Tools configuration
tools:
  # Path to drumsep directory
  drumsep_dir: "~/BestStemSplitter/drumsep"

# Output preferences
output:
  # Whether to organize output in folders by song name
  organize_by_song: true

  # Whether to include key and BPM in filename
  include_key_bpm: true

  # Format for output filenames
  filename_format: "{key} - {bpm}BPM - {name} - ({stem})"
```

## Usage

```
python stem_splitter.py <audio_file>
```

### Options:

- `-c`, `--config`: Path to custom config file
- `-o`, `--output`: Override output directory
- `-m`, `--model`: Override the Demucs model to use

### Available Demucs Models:

- `htdemucs`: Original HT model, 4 sources (vocals, drums, bass, other)
- `htdemucs_6s`: 6 sources model (adds piano and guitar separation)
- `htdemucs_ft`: Fine-tuned 4 sources model
- `mdx_extra`: Higher quality but slower
- `mdx_extra_q`: Quantized version of mdx_extra

### Examples:

```bash
# Split a song with default configuration
python stem_splitter.py my_song.mp3

# Use a custom config file
python stem_splitter.py my_song.mp3 --config my_config.yaml

# Specify output directory
python stem_splitter.py my_song.mp3 --output ~/Desktop/MySongStems

# Use a different model
python stem_splitter.py my_song.mp3 --model htdemucs

# Combine options
python stem_splitter.py my_song.mp3 --model mdx_extra --output ~/Desktop/HighQualityStems
```

## Important Note

This project requires PyTorch 2.5.1 or earlier to work properly with the drum separation model. The requirements.txt file specifies the correct version.

If you encounter any issues with model loading, you may need to set the following environment variable:

```bash
export TORCH_WEIGHTS_ONLY=0
<<<<<<< HEAD
```

=======

> > > > > > > ddee2710f5aba27dc4eacbbdfdfcb4651a7700e9

## Output

The script will create:

- A folder with your song's stems named according to your configuration
- Individual audio files for each stem (vocals, bass, drums, etc.)
- Individual drum component files (kick, snare, hats, toms)

## How It Works

1. The script analyzes your audio file to detect key and BPM
2. It uses Demucs to split the audio into stems
3. It uses Drumsep to separate drum components
4. All files are organized and named according to your preferences

## License

MIT License

## Acknowledgements

- [Demucs](https://github.com/facebookresearch/demucs) for audio source separation
- [Librosa](https://github.com/librosa/librosa) for audio analysis
- [drumSep](https://github.com/inagoy/drumsep) for drum separation
  <<<<<<< HEAD

```

=======
>>>>>>> ddee2710f5aba27dc4eacbbdfdfcb4651a7700e9
```
