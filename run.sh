#!/bin/bash
set -e  # Exit on error

echo "                          "
echo "=========================="
echo " Best Stem Splitter Ever! "
echo "--------------------------"
echo "Cobbled Together by TÂCHES"
echo "=========================="
echo "                          "

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again"
    exit 1
fi

if [ -z "$1" ]; then
  echo "Please provide an audio file to process."
  echo "Example: ./run.sh ~/Music/my_song.mp3"
  exit 1
fi

# Check if the file exists
if [ ! -f "$1" ]; then
  echo "❌ Error: File not found: $1"
  exit 1
fi

# Check for necessary dependencies
if [ ! -f "requirements.txt" ]; then
  echo "⚠️ Warning: requirements.txt not found"
else
  # Check if dependencies are installed
  if ! python3 -c "import librosa, yaml, demucs" &> /dev/null; then
    echo "⚠️ Missing dependencies. Running setup first..."
    bash setup.sh
  fi
fi

# Run the stem splitter
python3 stem_splitter.py "$1"