#!/usr/bin/env python3
"""
Video Transcoder Pipeline - Main Entry Point

This script provides a command-line interface for the video transcoding pipeline
that converts videos between 16:9 and 9:16 aspect ratios for multi-platform delivery.
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from video_transcoder import VideoTranscoder
from utils import setup_logging, validate_video_file

class VideoFileHandler(FileSystemEventHandler):
    """File system event handler for monitoring new video files."""
    
    def __init__(self, transcoder: VideoTranscoder):
        self.transcoder = transcoder
        self.logger = logging.getLogger(__name__)
        
    def on_created(self, event):
        """Handle new file creation events."""
        if event.is_directory:
            return
            
        file_path = event.src_path
        
        # Wait a moment for file to be fully written
        time.sleep(2)
        
        if validate_video_file(file_path):
            self.logger.info(f"New video detected: {file_path}")
            try:
                self.transcoder.process_video(file_path)
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")

def main():
    """Main entry point for the video transcoder pipeline."""
    
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description='Video Transcoder Pipeline - Convert videos between aspect ratios',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input video.mp4                    # Process single video
  %(prog)s --batch input/                       # Process all videos in directory
  %(prog)s --monitor input/                     # Monitor directory for new videos
  %(prog)s --monitor --input input/ --output output/  # Custom directories
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        help='Input video file or directory path'
    )
    
    parser.add_argument(
        '--output', '-o',
        default=os.getenv('OUTPUT_DIR', 'output'),
        help='Output directory (default: output/)'
    )
    
    parser.add_argument(
        '--temp-dir',
        default=os.getenv('TEMP_DIR', 'processing'),
        help='Temporary processing directory (default: processing/)'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Process all videos in input directory'
    )
    
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Monitor input directory for new videos'
    )
    
    parser.add_argument(
        '--video-bitrate',
        default=os.getenv('VIDEO_BITRATE', '2M'),
        help='Video bitrate for encoding (default: 2M)'
    )
    
    parser.add_argument(
        '--audio-bitrate',
        default=os.getenv('AUDIO_BITRATE', '128k'),
        help='Audio bitrate for encoding (default: 128k)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Video Transcoder Pipeline 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Validate arguments
    if not args.input and not args.monitor:
        parser.error("Must specify --input or --monitor")
    
    if args.monitor and not args.input:
        args.input = os.getenv('INPUT_DIR', 'input')
    
    # Initialize transcoder
    try:
        transcoder = VideoTranscoder(
            temp_dir=args.temp_dir,
            output_dir=args.output,
            video_bitrate=args.video_bitrate,
            audio_bitrate=args.audio_bitrate
        )
        logger.info("Video transcoder initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize transcoder: {e}")
        sys.exit(1)
    
    # Process videos based on mode
    try:
        if args.monitor:
            # Monitor mode
            input_path = Path(args.input)
            if not input_path.exists():
                logger.error(f"Input directory does not exist: {args.input}")
                sys.exit(1)
            
            logger.info(f"Starting monitor mode on directory: {args.input}")
            logger.info("Press Ctrl+C to stop monitoring...")
            
            event_handler = VideoFileHandler(transcoder)
            observer = Observer()
            observer.schedule(event_handler, str(input_path), recursive=True)
            observer.start()
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping monitor mode...")
                observer.stop()
            observer.join()
            
        elif args.batch:
            # Batch processing mode
            if not os.path.isdir(args.input):
                logger.error(f"Input path is not a directory: {args.input}")
                sys.exit(1)
            
            logger.info(f"Starting batch processing of directory: {args.input}")
            results = transcoder.batch_process(args.input)
            
            # Print summary
            logger.info("=== Processing Summary ===")
            logger.info(f"Successfully processed: {len(results['processed'])} videos")
            logger.info(f"Failed to process: {len(results['failed'])} videos")
            logger.info(f"Skipped: {len(results['skipped'])} videos")
            
            if results['failed']:
                logger.warning("Failed videos:")
                for failed in results['failed']:
                    logger.warning(f"  {failed['input']}: {failed['error']}")
        
        else:
            # Single file processing mode
            if not os.path.isfile(args.input):
                logger.error(f"Input file does not exist: {args.input}")
                sys.exit(1)
            
            logger.info(f"Processing single video: {args.input}")
            output_files = transcoder.process_video(args.input)
            
            logger.info("=== Processing Complete ===")
            logger.info(f"Input: {args.input}")
            logger.info("Output files:")
            for output_file in output_files:
                logger.info(f"  {output_file}")
    
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        sys.exit(1)
    
    logger.info("Video transcoding pipeline completed successfully")

if __name__ == '__main__':
    main()
