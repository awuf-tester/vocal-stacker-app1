# VocalStacker Pro

A local Windows desktop application for professional vocal stacking, cleaning, correction, harmonies, and stem separation.

## Features

- Import MP3, WAV, FLAC vocal tracks
- Add unlimited vocal takes with volume, pan, mute/solo controls
- Automatic vocal alignment and matching
- Vocal thickening, cleaning, pitch correction, harmony generation
- Stem separation via Demucs
- Real-time audio effects and export to WAV/MP3/FLAC
- Waveform visualization and playback preview

## Requirements

- Python 3.12+
- Windows PC
- FFmpeg installed for MP3 export with pydub

## Installation

1. Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Install FFmpeg or ensure it is on your PATH for MP3 export.

## Run

```powershell
python main.py
```

## Build with PyInstaller

```powershell
pyinstaller --noconfirm --onefile --windowed main.py
```

## Project Structure

- `main.py` - Application entry point
- `ui/` - CustomTkinter page modules
- `audio/` - Audio processing engine modules
- `ai/` - Pitch correction and stem separation
- `assets/` - Static resources
- `models/` - Local model storage path
- `temp/` - Temporary session files
- `exports/` - Exported audio files

## Deployment to Render

This repository includes a lightweight Flask backend and a Render manifest to deploy the audio-processing service.

Quick steps:

- Use `requirements-render.txt` for server dependencies.
- The WSGI entrypoint is `web:app` (see `web.py`).
- Start command (Render): `gunicorn web:app --workers 2 --bind 0.0.0.0:$PORT`

Environment variables to set on Render:

- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET` (optional for persistent storage)

Files and endpoints:

- `POST /upload` — multipart upload single audio file.
- `POST /stack/mix` — JSON body `{ "files": ["uploaded.wav"], "format": "wav" }` to mix tracks.
- `POST /separate` — JSON body `{ "file": "uploaded.wav" }` to run Demucs separation.
- `POST /pitch/correct` — JSON body `{ "file": "uploaded.wav", "strength": 0.6 }`.

See `render.yaml` for the sample service configuration.
