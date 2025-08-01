#!/usr/bin/env python3
"""
Example usage of the Video Transcoder Pipeline
"""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from video_transcoder import VideoTranscoder
from utils import setup_logging

def example_single_video():
    """Example: Process a single video file."""
    print("=== Example: Single Video Processing ===")
    
    # Setup logging
    setup_logging("INFO")
    
    # Initialize transcoder
    transcoder = VideoTranscoder(
        temp_dir="processing",
        output_dir="output",
        video_bitrate="2M",
        audio_bitrate="128k"
    )
    
    # Process a video (replace with actual video path)
    input_video = "input/sample_video.mp4"
    
    if os.path.exists(input_video):
        try:
            output_files = transcoder.process_video(input_video)
            print(f"Successfully processed video!")
            print("Output files:")
            for file in output_files:
                print(f"  - {file}")
        except Exception as e:
            print(f"Error processing video: {e}")
    else:
        print(f"Sample video not found: {input_video}")
        print("Please add a sample video to the input/ directory")

def example_batch_processing():
    """Example: Batch process all videos in a directory."""
    print("\n=== Example: Batch Processing ===")
    
    # Setup logging
    setup_logging("INFO")
    
    # Initialize transcoder
    transcoder = VideoTranscoder()
    
    # Process all videos in input directory
    input_dir = "input"
    
    if os.path.exists(input_dir):
        try:
            results = transcoder.batch_process(input_dir)
            
            print("Batch processing completed!")
            print(f"Processed: {len(results['processed'])} videos")
            print(f"Failed: {len(results['failed'])} videos")
            print(f"Skipped: {len(results['skipped'])} videos")
            
            if results['processed']:
                print("\nSuccessfully processed:")
                for item in results['processed']:
                    print(f"  - {item['input']} → {len(item['outputs'])} outputs")
            
            if results['failed']:
                print("\nFailed to process:")
                for item in results['failed']:
                    print(f"  - {item['input']}: {item['error']}")
                    
        except Exception as e:
            print(f"Batch processing error: {e}")
    else:
        print(f"Input directory not found: {input_dir}")

def example_monitor_mode():
    """Example: Monitor directory for new videos."""
    print("\n=== Example: Monitor Mode ===")
    print("To run monitor mode, use the CLI:")
    print("python main.py --monitor --input input/")
    print("\nThis will watch the input/ directory for new videos and process them automatically.")
    print("Press Ctrl+C to stop monitoring.")

if __name__ == "__main__":
    print("Video Transcoder Pipeline - Usage Examples")
    print("=" * 50)
    
    example_single_video()
    example_batch_processing()
    example_monitor_mode()
    
    print("\n" + "=" * 50)
    print("For more options, run: python main.py --help")
