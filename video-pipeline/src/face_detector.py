import cv2
import numpy as np
import logging
import os
from typing import Tuple, List, Optional

class FaceDetector:
    """Face detection utility for intelligent video cropping."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize face detector.
        
        Args:
            model_path: Path to Haar cascade model file
        """
        self.logger = logging.getLogger(__name__)
        
        # Try to load face detection model
        try:
            if model_path and os.path.exists(model_path):
                self.face_cascade = cv2.CascadeClassifier(model_path)
            else:
                # Use built-in OpenCV model
                self.face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
            
            if self.face_cascade.empty():
                raise RuntimeError("Failed to load face detection model")
                
            self.logger.info("Face detector initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize face detector: {e}")
            self.face_cascade = None
    
    def detect_faces_in_frame(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in a single frame.
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            List of face bounding boxes (x, y, w, h)
        """
        if self.face_cascade is None:
            return []
        
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            return [(int(x), int(y), int(w), int(h)) for x, y, w, h in faces]
            
        except Exception as e:
            self.logger.warning(f"Face detection failed for frame: {e}")
            return []
    
    def get_optimal_crop_center(self, video_path: str, target_aspect: float = 9/16) -> Tuple[int, int]:
        """
        Analyze video frames to find optimal crop center based on face positions.
        
        Args:
            video_path: Path to video file
            target_aspect: Target aspect ratio (height/width)
            
        Returns:
            Tuple of (center_x, center_y) for optimal crop
        """
        if self.face_cascade is None:
            self.logger.warning("Face detector not available, using center crop")
            return self._get_center_crop(video_path)
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError(f"Cannot open video: {video_path}")
            
            # Get video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Sample frames throughout the video
            sample_frames = min(20, frame_count)  # Sample up to 20 frames
            frame_indices = np.linspace(0, frame_count - 1, sample_frames, dtype=int)
            
            all_face_centers = []
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                faces = self.detect_faces_in_frame(frame)
                
                # Calculate center points of detected faces
                for x, y, w, h in faces:
                    center_x = x + w // 2
                    center_y = y + h // 2
                    all_face_centers.append((center_x, center_y))
            
            cap.release()
            
            if all_face_centers:
                # Calculate average face center
                avg_x = int(np.mean([x for x, y in all_face_centers]))
                avg_y = int(np.mean([y for x, y in all_face_centers]))
                
                # Ensure crop center is within valid bounds
                crop_width = int(height * target_aspect)
                crop_height = height
                
                # Adjust center to ensure crop doesn't go outside frame
                min_x = crop_width // 2
                max_x = width - crop_width // 2
                min_y = crop_height // 2
                max_y = height - crop_height // 2
                
                center_x = max(min_x, min(max_x, avg_x))
                center_y = max(min_y, min(max_y, avg_y))
                
                self.logger.info(f"Found {len(all_face_centers)} face detections, using center: ({center_x}, {center_y})")
                return center_x, center_y
            
            else:
                self.logger.info("No faces detected, using center crop")
                return self._get_center_crop(video_path)
                
        except Exception as e:
            self.logger.error(f"Error in face-based crop analysis: {e}")
            return self._get_center_crop(video_path)
    
    def _get_center_crop(self, video_path: str) -> Tuple[int, int]:
        """
        Get center crop position as fallback.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Tuple of (center_x, center_y)
        """
        try:
            cap = cv2.VideoCapture(video_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            return width // 2, height // 2
            
        except Exception as e:
            self.logger.error(f"Failed to get video dimensions: {e}")
            return 640, 360  # Fallback values
