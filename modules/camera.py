"""
Camera Module
Handles webcam operations and video frame capture.
"""

import cv2


class Camera:
    """Class to handle camera operations."""
    
    def __init__(self, camera_index=0):
        """
        Initialize Camera.
        
        Args:
            camera_index (int): Camera device index (usually 0 for default)
        """
        self.camera_index = camera_index
        self.camera = None
    
    def open_camera(self):
        """
        Open camera connection.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                return False
            return True
        except Exception as e:
            print(f"Error opening camera: {e}")
            return False
    
    def read_frame(self):
        """
        Read a frame from the camera.
        
        Returns:
            tuple: (success, frame) where success is bool and frame is numpy array
        """
        if self.camera is None:
            return False, None
        
        success, frame = self.camera.read()
        return success, frame
    
    def release_camera(self):
        """Release camera resources."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
    
    def is_opened(self):
        """
        Check if camera is opened.
        
        Returns:
            bool: True if camera is opened, False otherwise
        """
        return self.camera is not None and self.camera.isOpened()

