# RealESRGAN GUI Wrapper

A dedicated Python GUI for [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) designed specifically for video upscaling stability. 

Unlike other GUIs that might cause audio desync or variable framerate issues, this tool uses a "Strict Sync" method: it deconstructs video into frames, upscales them, and rebuilds the video using the **exact** source framerate and audio stream.

## Features

- **Strict Sync Mode:** Forces constant frame rate (CFR) to prevent audio desync.
- **Progress Tracking:** Real-time log output and progress bar.
- **Image & Video Support:** Upscale single images or full videos.
- **Model Selection:** Support for `realesr-animevideov3`, `realesrgan-x4plus`, and more.
- **Hardware Agnostic:** Works with whatever RealESRGAN binary you provide (NCNN/Vulkan supported).

## Prerequisites

This application is a GUI wrapper. For it to work, you must have the following installed on your system:

1. **FFmpeg**: Must be installed and added to your system PATH.
   - To test, open a terminal and type: `ffmpeg -version`
2. **RealESRGAN Executable**: You need the command-line binary.
   - **Tested Version:** `realesrgan-ncnn-vulkan-20220424-windows` (v0.2.0.0).
   - [Download it here](https://github.com/xinntao/Real-ESRGAN/releases/tag/v0.2.0.0)

## Installation

### Option A: Download Binary (Windows)
1. Go to the [Releases](https://github.com/Kuldeep-Dilliwar/realesrgan-gui-wrapper/releases) page.
2. Download `RealESRGAN-Strict-GUI-Windows.zip`.
3. Extract and run the `.exe`.

### Option B: Run from Source
1. Clone the repository.
2. Install Python 3.x.
3. Run the script:
   ```bash
   python main.py
