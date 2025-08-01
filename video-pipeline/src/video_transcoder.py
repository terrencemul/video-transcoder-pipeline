import os
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import ffmpeg

from .utils import (
    get_video_dimensions, 
    determine_aspect_ratio, 
    get_output_filename,
    ensure_directory,
    cleanup_temp_files,
    validate_video_file
)
from .face_detector import FaceDetector

class VideoTranscoder:
    """Main video transcoding pipeline for aspect ratio conversion."""
    
    def __init__(self, 
                 temp_dir: str = "processing",
                 output_dir: str = "output",
                 video_bitrate: str = "2M",
                 audio_bitrate: str = "128k"):
        """
        Initialize video transcoder.
        
        Args:
            temp_dir: Temporary processing directory
            output_dir: Output directory for final files
            video_bitrate: Video bitrate for encoding
            audio_bitrate: Audio bitrate for encoding
        """
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        self.video_bitrate = video_bitrate
        self.audio_bitrate = audio_bitrate
        
        self.logger = logging.getLogger(__name__)
        self.face_detector = FaceDetector()
        
        # Ensure directories exist
        ensure_directory(self.temp_dir)
        ensure_directory(self.output_dir)
        
        self.logger.info("VideoTranscoder initialized")
    
    def process_video(self, input_path: str) -> list[str]:
        """
        Process a single video file, creating both aspect ratio versions.
        
        Args:
            input_path: Path to input video file
            
        Returns:
            List of output file paths created
        """
        if not validate_video_file(input_path):
            raise ValueError(f"Invalid video file: {input_path}")
        
        self.logger.info(f"Processing video: {input_path}")
        
        try:
            # Get video dimensions and determine original aspect ratio
            width, height = get_video_dimensions(input_path)
            original_aspect = determine_aspect_ratio(width, height)
            
            self.logger.info(f"Video dimensions: {width}x{height}, aspect ratio: {original_aspect}")
            
            output_files = []
            
            # Keep original aspect ratio version
            original_output = self._create_original_version(input_path, original_aspect)
            if original_output:
                output_files.append(original_output)
            
            # Create converted aspect ratio version
            converted_output = self._create_converted_version(input_path, original_aspect, width, height)
            if converted_output:
                output_files.append(converted_output)
            
            self.logger.info(f"Successfully processed video. Created {len(output_files)} output files.")
            return output_files
            
        except Exception as e:
            self.logger.error(f"Failed to process video {input_path}: {e}")
            raise
    
    def _create_original_version(self, input_path: str, aspect_ratio: str) -> Optional[str]:
        """
        Create a copy of the original video with proper naming.
        
        Args:
            input_path: Path to input video
            aspect_ratio: Original aspect ratio
            
        Returns:
            Path to output file or None if failed
        """
        try:
            output_filename = get_output_filename(input_path, aspect_ratio)
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Simple copy with re-encoding for consistency
            (
                ffmpeg
                .input(input_path)
                .output(
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    video_bitrate=self.video_bitrate,
                    audio_bitrate=self.audio_bitrate,
                    movflags='faststart'
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            self.logger.info(f"Created original version: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to create original version: {e}")
            return None
    
    def _create_converted_version(self, input_path: str, original_aspect: str, width: int, height: int) -> Optional[str]:
        """
        Create converted aspect ratio version.
        
        Args:
            input_path: Path to input video
            original_aspect: Original aspect ratio
            width: Original video width
            height: Original video height
            
        Returns:
            Path to output file or None if failed
        """
        if original_aspect == "16:9":
            return self._convert_16_9_to_9_16(input_path, width, height)
        else:
            return self._convert_9_16_to_16_9(input_path, width, height)
    
    def _convert_16_9_to_9_16(self, input_path: str, width: int, height: int) -> Optional[str]:
        """
        Convert 16:9 video to 9:16 with face-centered cropping.
        
        Args:
            input_path: Path to input video
            width: Original video width
            height: Original video height
            
        Returns:
            Path to output file or None if failed
        """
        try:
            output_filename = get_output_filename(input_path, "9:16")
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Calculate crop dimensions for 9:16
            target_width = int(height * (9/16))
            
            if target_width > width:
                # If calculated width is larger than source, use full width and adjust height
                target_width = width
                target_height = int(width * (16/9))
                crop_x = 0
                crop_y = (height - target_height) // 2
            else:
                # Use face detection to determine optimal crop center
                center_x, center_y = self.face_detector.get_optimal_crop_center(input_path, 16/9)
                
                # Calculate crop position
                crop_x = max(0, min(width - target_width, center_x - target_width // 2))
                crop_y = 0
                target_height = height
            
            self.logger.info(f"Cropping 16:9 to 9:16: crop at ({crop_x}, {crop_y}), size {target_width}x{target_height}")
            
            # Apply crop and scale to standard 9:16 resolution (1080x1920)
            (
                ffmpeg
                .input(input_path)
                .filter('crop', target_width, target_height, crop_x, crop_y)
                .filter('scale', 1080, 1920)
                .output(
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    video_bitrate=self.video_bitrate,
                    audio_bitrate=self.audio_bitrate,
                    movflags='faststart'
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            self.logger.info(f"Created 9:16 version: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to convert 16:9 to 9:16: {e}")
            return None
    
    def _convert_9_16_to_16_9(self, input_path: str, width: int, height: int) -> Optional[str]:
        """
        Convert 9:16 video to 16:9 with blurred letterbox bars.
        
        Args:
            input_path: Path to input video
            width: Original video width
            height: Original video height
            
        Returns:
            Path to output file or None if failed
        """
        try:
            output_filename = get_output_filename(input_path, "16:9")
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Target 16:9 resolution (1920x1080)
            target_width = 1920
            target_height = 1080
            
            # Calculate scaling for the main video (maintain aspect ratio)
            scale_factor = min(target_width / width, target_height / height)
            scaled_width = int(width * scale_factor)
            scaled_height = int(height * scale_factor)
            
            # Calculate positioning (center the video)
            x_offset = (target_width - scaled_width) // 2
            y_offset = (target_height - scaled_height) // 2
            
            self.logger.info(f"Converting 9:16 to 16:9: scaling to {scaled_width}x{scaled_height}, offset ({x_offset}, {y_offset})")
            
            # Create blurred background and overlay main video
            main_video = ffmpeg.input(input_path)
            
            # Create blurred background (scaled and heavily blurred)
            background = (
                main_video
                .filter('scale', target_width, target_height)
                .filter('gblur', sigma=50)
            )
            
            # Scale main video to fit
            foreground = (
                main_video
                .filter('scale', scaled_width, scaled_height)
            )
            
            # Overlay main video on blurred background
            output_stream = ffmpeg.overlay(background, foreground, x=x_offset, y=y_offset)
            
            (
                output_stream
                .output(
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    video_bitrate=self.video_bitrate,
                    audio_bitrate=self.audio_bitrate,
                    movflags='faststart'
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            self.logger.info(f"Created 16:9 version: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to convert 9:16 to 16:9: {e}")
            return None
    
    def batch_process(self, input_dir: str) -> dict:
        """
        Process all videos in input directory.
        
        Args:
            input_dir: Directory containing input videos
            
        Returns:
            Dictionary with processing results
        """
        results = {
            'processed': [],
            'failed': [],
            'skipped': []
        }
        
        input_path = Path(input_dir)
        if not input_path.exists():
            raise ValueError(f"Input directory does not exist: {input_dir}")
        
        # Find all video files
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.m4v'}
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(input_path.glob(f'**/*{ext}'))
            video_files.extend(input_path.glob(f'**/*{ext.upper()}'))
        
        self.logger.info(f"Found {len(video_files)} video files to process")
        
        for video_file in video_files:
            try:
                if validate_video_file(str(video_file)):
                    output_files = self.process_video(str(video_file))
                    results['processed'].append({
                        'input': str(video_file),
                        'outputs': output_files
                    })
                else:
                    results['skipped'].append(str(video_file))
                    
            except Exception as e:
                self.logger.error(f"Failed to process {video_file}: {e}")
                results['failed'].append({
                    'input': str(video_file),
                    'error': str(e)
                })
        
        # Cleanup temp files
        cleanup_temp_files(self.temp_dir)
        
        return results
