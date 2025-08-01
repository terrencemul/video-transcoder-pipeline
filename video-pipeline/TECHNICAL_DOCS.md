# Video Transcoder Pipeline - Technical Documentation

## Architecture Overview

The Video Transcoder Pipeline is designed as a modular system with the following components:

### Core Modules

#### 1. `VideoTranscoder` (video_transcoder.py)
Main transcoding engine that handles:
- Aspect ratio detection and conversion
- File management and output naming
- FFmpeg integration for video processing

**Key Methods:**
- `process_video(input_path)` - Process single video
- `batch_process(input_dir)` - Process directory of videos
- `_convert_16_9_to_9_16()` - Convert horizontal to vertical with face cropping
- `_convert_9_16_to_16_9()` - Convert vertical to horizontal with blur letterbox

#### 2. `FaceDetector` (face_detector.py)
Intelligent cropping using OpenCV face detection:
- Analyzes multiple frames throughout video
- Calculates optimal crop center based on face positions
- Fallback to center crop if no faces detected

**Key Methods:**
- `detect_faces_in_frame(frame)` - Detect faces in single frame
- `get_optimal_crop_center(video_path)` - Analyze video for best crop position

#### 3. `Utils` (utils.py)
Helper functions for:
- Video dimension analysis
- File validation and naming
- Directory management
- Logging setup

## Processing Workflow

### 1. Input Analysis
```
Video File → FFprobe → Dimensions → Aspect Ratio Determination
```

### 2. Conversion Logic

#### 16:9 → 9:16 Conversion
1. **Face Detection**: Analyze sample frames for face positions
2. **Crop Calculation**: Determine optimal crop area (9:16 from 16:9)
3. **Face Centering**: Position crop to keep faces centered
4. **Scale**: Resize to standard 1080x1920 (9:16)

#### 9:16 → 16:9 Conversion  
1. **Background Creation**: Scale and blur original video to 1920x1080
2. **Foreground Scaling**: Scale original video to fit within 16:9 while maintaining aspect ratio
3. **Overlay**: Center scaled video on blurred background

### 3. Output Generation
Both formats are always generated:
- Original aspect ratio with platform naming
- Converted aspect ratio with platform naming

## File Naming Convention

### Input Processing
Any video file: `video.mp4`

### Output Generation
- **16:9 version**: `video_16x9_youtube_googlebusiness_instagram.mp4`
- **9:16 version**: `video_9x16_tiktok_instastories_youtubeshorts_instagram.mp4`

## Platform Mapping

| Aspect Ratio | Platforms |
|--------------|-----------|
| 16:9 | YouTube, Google Business, Instagram Feed |
| 9:16 | TikTok, Instagram Stories, YouTube Shorts, Instagram Feed |

## Configuration

### Environment Variables (.env)
```env
# Processing
TEMP_DIR=processing
OUTPUT_DIR=output
INPUT_DIR=input

# Quality
VIDEO_BITRATE=2M
AUDIO_BITRATE=128k

# Face Detection
FACE_DETECTION_MODEL=haarcascade_frontalface_alt.xml
FACE_PADDING=0.2

# Performance
MAX_CONCURRENT_JOBS=2
CLEANUP_TEMP_FILES=true
```

### Video Quality Settings
- **Video Codec**: H.264 (libx264)
- **Audio Codec**: AAC
- **Bitrates**: Configurable (default 2M video, 128k audio)
- **Container**: MP4 with faststart flag for web optimization

## API Reference

### VideoTranscoder Class

```python
from src.video_transcoder import VideoTranscoder

# Initialize
transcoder = VideoTranscoder(
    temp_dir="processing",
    output_dir="output", 
    video_bitrate="2M",
    audio_bitrate="128k"
)

# Process single video
output_files = transcoder.process_video("input/video.mp4")

# Batch process
results = transcoder.batch_process("input/")
```

### FaceDetector Class

```python
from src.face_detector import FaceDetector

# Initialize
detector = FaceDetector()

# Get optimal crop center
center_x, center_y = detector.get_optimal_crop_center("video.mp4")

# Detect faces in frame
faces = detector.detect_faces_in_frame(frame_array)
```

### Utility Functions

```python
from src.utils import *

# Get video info
width, height = get_video_dimensions("video.mp4")
aspect = determine_aspect_ratio(width, height)

# File operations
is_valid = validate_video_file("video.mp4")
output_name = get_output_filename("video.mp4", "16:9")

# Setup
setup_logging("INFO")
ensure_directory("output/")
```

## CLI Usage

### Basic Commands
```bash
# Single file
python main.py --input video.mp4

# Batch processing
python main.py --batch --input input/

# Monitor mode (watch for new files)
python main.py --monitor --input input/

# Custom settings
python main.py --input video.mp4 --output custom_output/ --video-bitrate 4M
```

### Monitor Mode
Monitor mode uses the `watchdog` library to watch for new files:
- Monitors recursively including subdirectories
- Processes files after 2-second delay (allows complete upload)
- Continues running until Ctrl+C

## Error Handling

### Common Issues
1. **FFmpeg not found**: Install FFmpeg and add to PATH
2. **Invalid video format**: Check file extension and codec
3. **Face detection failure**: Falls back to center crop
4. **Insufficient disk space**: Check temp and output directories
5. **Permission errors**: Ensure write access to output directories

### Logging
- **INFO**: General processing information
- **WARNING**: Non-fatal issues (face detection failures, etc.)
- **ERROR**: Processing failures
- **DEBUG**: Detailed execution information

Logs are written to both console and `video_pipeline.log` file.

## Performance Considerations

### Processing Speed
- Face detection adds ~10-15% processing time
- Blur letterbox effect is computationally intensive
- Batch processing is more efficient than individual files

### Resource Usage
- **CPU**: High during transcoding (FFmpeg)
- **Memory**: Moderate for face detection (OpenCV)
- **Disk**: 2-3x input file size for temporary processing

### Optimization Tips
1. Use SSD for temp directory
2. Adjust video bitrate based on quality needs
3. Limit concurrent jobs on lower-end hardware
4. Monitor disk space in production

## Integration with n8n Workflow

The pipeline is designed to integrate with n8n workflows:

### Input Structure
```
input/
├── short_form_9_16/        # From n8n: vertical videos
├── long_form_16_9_or_9_16/ # From n8n: mixed format videos  
└── listings_16_9/          # From n8n: horizontal videos
```

### n8n Integration Points
1. **File Drop**: n8n uploads videos to appropriate input folders
2. **Processing Trigger**: Monitor mode or scheduled batch processing
3. **Output Consumption**: Other systems read output files based on naming convention

## Deployment

### Local Development
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install FFmpeg
4. Run setup test: `python test_setup.py`

### Production Deployment
1. Use virtual environment
2. Configure `.env` for production paths
3. Set up monitoring/logging
4. Consider containerization (Docker)
5. Implement error alerting

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9
RUN apt-get update && apt-get install -y ffmpeg
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["python", "main.py", "--monitor"]
```

## Extensibility

### Adding New Platforms
Modify `get_output_filename()` in `utils.py`:
```python
if aspect_ratio == "16:9":
    suffix = "_16x9_youtube_googlebusiness_instagram_newplatform"
```

### Custom Aspect Ratios
Extend `determine_aspect_ratio()` and add conversion methods:
```python
def _convert_16_9_to_1_1(self, input_path, width, height):
    # Square format conversion
    pass
```

### Advanced Face Detection
Replace OpenCV with more advanced models:
- MediaPipe Face Detection
- MTCNN
- Custom trained models

## Testing

### Unit Tests
Run individual component tests:
```bash
python -m pytest tests/
```

### Integration Tests
Test full pipeline with sample videos:
```bash
python test_setup.py
python example_usage.py
```

### Performance Tests
Benchmark processing speed:
```bash
python -m cProfile main.py --input large_video.mp4
```
