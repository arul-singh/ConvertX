# ConvertX Studio

A simple, fast desktop application for batch file conversions. It runs completely locally on your machine, meaning your files are never uploaded to a third-party server or cloud service.

Built using Python and PyQt6 for a native, responsive user interface.

## Core Features

* Drag and Drop: Drop multiple files directly into the window from your desktop or file manager to queue them up.
* Smart Extension Filtering: The application scans the files you load and automatically filters the available output formats (e.g., loading only images will restrict the dropdown to image formats).
* Custom Output Folders: Save converted files directly alongside the originals, or pick a specific directory to keep things organized.
* Completely Private: Runs entirely offline with no telemetries or tracking.

## Supported Formats

* Documents: docx, pdf, odt, rtf, txt, html, epub
* Markup: md, tex, rst, ipynb, json, xml, csv
* Images: png, jpg, jpeg, webp, bmp, gif, tiff, ico
* Audio: mp3, wav, m4a, flac, ogg, aac
* Video: mp4, mkv, avi, mov, webm

## How to Setup and Run Locally

### Prerequisites

* Python 3.10 or higher
* ffmpeg and pandoc installed on your system path (required for audio/video and complex document routing).

NOTE: You do not need to pre-install libraries like PyQt6, Pillow, or pdf2docx manually. The installation steps below will handle all of them automatically
### Installation

1. Clone this repository:
```bash
git clone https://github.com/arul-singh/ConvertX.git
cd ConvertX
```

2. Create and activate a virtual environment:
```bash

python3 -m venv .venv
source .venv/bin/activate
```

3. Install the required libraries:
```bash
python3 -m pip install -r requirements.txt
```
4. Run the app:
```bash
python3 app.py
```
## License

MIT License - feel free to use and modify this tool however you like.
