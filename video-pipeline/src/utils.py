import os
import logging
from pathlib import Path
from typing import Tuple, Optional

def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('video_pipeline.log'),
            logging.StreamHandler()
        ]
    )

def get_video_dimensions(video_path: str) -> Tuple[int, int]:
    """
    Get video dimensions using ffprobe.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Tuple of (width, height)
    """
    import subprocess
    import json
    
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        # Find video stream
        for stream in data['streams']:
            if stream['codec_type'] == 'video':
                return int(stream['width']), int(stream['height'])
        
        raise ValueError("No video stream found")
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get video dimensions: {e}")
    except Exception as e:
        raise RuntimeError(f"Error processing video info: {e}")

def determine_aspect_ratio(width: int, height: int) -> str:
    """
    Determine if video is 16:9 or 9:16 (or closest match).
    
    Args:
        width: Video width
        height: Video height
        
    Returns:
        '16:9' or '9:16'
    """
    ratio = width / height
    
    # 16:9 = 1.778, 9:16 = 0.5625
    if ratio > 1.2:  # More horizontal than square
        return "16:9"
    else:  # More vertical than square
        return "9:16"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for cross-platform compatibility.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove problematic characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove extra spaces and dots
    filename = ' '.join(filename.split())
    filename = filename.strip('.')
    
    return filename

def ensure_directory(path: str) -> None:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path
    """
    Path(path).mkdir(parents=True, exist_ok=True)

def get_output_filename(original_path: str, aspect_ratio: str) -> str:
    """
    Generate output filename with platform suffixes.
    
    Args:
        original_path: Original video file path
        aspect_ratio: Target aspect ratio ('16:9' or '9:16')
        
    Returns:
        New filename with platform suffix
    """
    path = Path(original_path)
    base_name = path.stem
    
    if aspect_ratio == "16:9":
        suffix = "_16x9_youtube_googlebusiness_instagram"
    else:  # 9:16
        suffix = "_9x16_tiktok_instastories_youtubeshorts_instagram"
    
    return f"{base_name}{suffix}.mp4"

def cleanup_temp_files(temp_dir: str, keep_pattern: Optional[str] = None) -> None:
    """
    Clean up temporary files in processing directory.
    
    Args:
        temp_dir: Temporary directory path
        keep_pattern: Pattern of files to keep (optional)
    """
    try:
        temp_path = Path(temp_dir)
        if not temp_path.exists():
            return
            
        for file_path in temp_path.iterdir():
            if file_path.is_file():
                if keep_pattern is None or keep_pattern not in str(file_path):
                    file_path.unlink()
                    logging.debug(f"Cleaned up temp file: {file_path}")
                    
    except Exception as e:
        logging.warning(f"Failed to cleanup temp files: {e}")

def validate_video_file(file_path: str) -> bool:
    """
    Validate if file is a supported video format.
    
    Args:
        file_path: Path to video file
        
    Returns:
        True if valid video file
    """
    supported_formats = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.m4v'}
    
    path = Path(file_path)
    
    # Check if file exists
    if not path.exists():
        return False
    
    # Check file extension
    if path.suffix.lower() not in supported_formats:
        return False
    
    # Check if file is not empty
    if path.stat().st_size == 0:
        return False
    
    return True
