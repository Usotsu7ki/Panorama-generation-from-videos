# Panorama Generator

This is a Python-based panorama generation tool that can extract key frames from videos and generate panoramic images. The tool provides an intuitive graphical user interface, allowing users to easily process videos and generate high-quality panoramas.

## Project Structure

```
.
├── gui.py                 # Main GUI program
├── get_key_frames.py      # Key frame extraction module
├── pano_generation.py     # Panorama generation module
├── requirements.txt       # Project dependencies
├── key_frames/           # Key frames storage directory
└── *.mp4, *.jpg          # Sample video and image files
```

## Requirements

- see requirements.txt

## Installation

1. Clone this project 
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the GUI program:
   ```bash
   python gui.py
   ```

2. Operation steps:
   - Click the "Select Video" button to choose a video file
   - Set the stride parameter for key frame extraction
   - Enter a name for the panorama (default is "panorama")
   - Click "Get Key Frames" to extract key frames
   - After extraction, click "Open Key Frames Folder" to view the extracted frames
   - Click "Generate Panorama" to create the panorama
   - The generated panorama will be displayed in the preview area
   - Click "Reset" to start over if needed

## Features

- **Video Selection**: Supports common video formats like MP4, AVI, MOV
- **Key Frame Extraction**: Controls frame extraction frequency through stride parameter
- **Panorama Generation**: Automatically stitches extracted key frames into a panorama
- **Real-time Preview**: Generated panorama can be previewed in the interface
- **Folder Browsing**: Direct access to view extracted key frames

## Notes

1. Ensure video file paths do not contain Chinese characters
2. Use clear and stable video sources for better panorama results
3. The stride parameter affects final panorama quality, adjust according to video content
4. Panorama generation may take some time, please be patient

## Dependencies

- PyQt5: For building the graphical user interface
- OpenCV: For video and image processing
- NumPy: For numerical computations
- imutils: For image processing utilities 