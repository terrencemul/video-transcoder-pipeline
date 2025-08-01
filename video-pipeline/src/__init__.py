"""
Video Transcoder Pipeline - Source Package

This package contains the core video transcoding functionality for converting
videos between 16:9 and 9:16 aspect ratios with intelligent cropping and
blurred letterbox effects.
"""

from .video_transcoder import VideoTranscoder
from .face_detector import FaceDetector
from .utils import (
    get_video_dimensions,
    determine_aspect_ratio,
    get_output_filename,
    validate_video_file,
    setup_logging
)

__version__ = "1.0.0"
__author__ = "Video Pipeline Team"

__all__ = [
    'VideoTranscoder',
    'FaceDetector', 
    'get_video_dimensions',
    'determine_aspect_ratio',
    'get_output_filename',
    'validate_video_file',
    'setup_logging'
]
