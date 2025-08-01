# Video Transcoder Pipeline

A video transcoding pipeline that automatically converts videos between aspect ratios (16:9 ↔ 9:16) and organizes them for multi-platform delivery.

## Features

- **Smart Aspect Ratio Conversion**: 
  - 16:9 → 9:16 with face detection and intelligent cropping
  - 9:16 → 16:9 with blurred letterbox bars
- **Platform-Specific Naming**: Automatically appends destination platforms to filenames
- **Batch Processing**: Monitors input folder for new videos
- **Face Detection**: Uses OpenCV for centering faces during 16:9 to 9:16 conversion

## Input Sources

Videos are processed from three categories:
- `short_form_9:16` - Vertical videos
- `long_form_16:9_or_9:16` - Mixed format videos  
- `listings_16:9` - Horizontal videos

## Output Naming Convention

- **16:9 versions** → `_youtube_googlebusiness_instagram.mp4`
- **9:16 versions** → `_tiktok_instastories_youtubeshorts_instagram.mp4`

Example:
```
Input: video1.mp4
Output: 
- video1_16x9_youtube_googlebusiness_instagram.mp4
- video1_9x16_tiktok_instastories_youtubeshorts_instagram.mp4
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install FFmpeg:
   - Windows: Download from https://ffmpeg.org/download.html
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

3. Create configuration file:
```bash
cp .env.example .env
```

## Usage

### Single Video Processing
```python
from video_transcoder import VideoTranscoder

transcoder = VideoTranscoder()
transcoder.process_video('input/video.mp4')
```

### Batch Processing (Monitor Mode)
```bash
python main.py --monitor
```

### CLI Processing
```bash
python main.py --input "input/video.mp4"
```

## Project Structure

```
video-pipeline/
├── input/              # Videos from n8n workflow
│   ├── short_form_9:16/
│   ├── long_form_16:9_or_9:16/
│   └── listings_16:9/
├── processing/         # Temporary processing folder
├── output/            # Final files with destination naming
├── src/
│   ├── video_transcoder.py    # Main transcoding logic
│   ├── face_detector.py       # Face detection utilities
│   └── utils.py              # Helper functions
├── main.py            # CLI entry point
├── requirements.txt   # Python dependencies
└── .env              # Configuration file
```

## Configuration

Edit `.env` file to customize:

```env
# Processing settings
TEMP_DIR=processing
OUTPUT_DIR=output
INPUT_DIR=input

# Video quality settings
VIDEO_BITRATE=2M
AUDIO_BITRATE=128k

# Face detection settings
FACE_DETECTION_MODEL=haarcascade_frontalface_alt.xml
FACE_PADDING=0.2
```

## Platform Delivery

The transcoded files are named for automated delivery to:
- **Google Business** (16:9)
- **TikTok** (9:16)
- **Instagram Feed** (both formats)
- **Instagram Stories** (9:16)
- **YouTube** (16:9)
- **YouTube Shorts** (9:16)

## License

MIT License
