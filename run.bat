@echo off
echo BestStemSplitterEver
echo ===================

REM Check if Python is installed
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo X Error: Python is not installed or not in PATH
  echo Please install Python and try again
  pause
  exit /b 1
)

if "%~1"=="" (
  echo Please drag and drop an audio file onto this batch file
  echo or specify a file as an argument.
  echo.
  echo Example: run.bat "C:\Music\my_song.mp3"
  pause
  exit /b 1
)

REM Check if the file exists
if not exist "%~1" (
  echo X Error: File not found: %1
  pause
  exit /b 1
)

REM Check for necessary dependencies
python -c "import librosa, yaml, demucs" > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo Warning: Missing dependencies. Running setup first...
  call setup.bat
)

REM Run the stem splitter
python stem_splitter.py "%~1"
pause