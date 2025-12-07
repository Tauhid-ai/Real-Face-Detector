"""
Face Encoder Module
Handles face encoding and recognition using OpenCV (no heavy dependencies).
"""

import cv2
import numpy as np
import os
import pickle


class FaceEncoder:
    """Class to handle face encoding and recognition using OpenCV."""
    
    def __init__(self, faces_dir='static/faces'):
        """
        Initialize FaceEncoder.
        
        Args:
            faces_dir (str): Directory to store face images
        """
        self.faces_dir = faces_dir
        self.ensure_directory()
        # Load face detector (Haar Cascade - lightweight and built into OpenCV)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
    
    def ensure_directory(self):
        """Ensure the faces directory exists."""
        if not os.path.exists(self.faces_dir):
            os.makedirs(self.faces_dir)
    
    def detect_face(self, image):
        """
        Detect face in an image using OpenCV.
        
        Args:
            image: Image array (BGR format from OpenCV)
            
        Returns:
            list: List of face rectangles [(x, y, w, h), ...] or empty list
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return faces
    
    def create_face_encoding(self, face_gray):
        """
        Create face encoding from grayscale face image.
        
        Args:
            face_gray: Grayscale face image (numpy array)
            
        Returns:
            numpy.ndarray: Face encoding
        """
        # Resize to standard size for comparison
        face_resized = cv2.resize(face_gray, (128, 128))
        
        # Apply histogram equalization for better contrast
        face_eq = cv2.equalizeHist(face_resized)
        
        # Create histogram features
        hist = cv2.calcHist([face_eq], [0], None, [256], [0, 256])
        hist = hist.flatten()
        hist = hist / (hist.sum() + 1e-7)
        
        # Divide face into 9 regions for spatial features
        h, w = face_eq.shape
        regions = []
        for i in range(3):
            for j in range(3):
                y1, y2 = i * h // 3, (i + 1) * h // 3
                x1, x2 = j * w // 3, (j + 1) * w // 3
                region = face_eq[y1:y2, x1:x2]
                regions.append(region.mean())
                regions.append(region.std())
        
        # Add edge features using Canny
        edges = cv2.Canny(face_eq, 50, 150)
        edge_hist = cv2.calcHist([edges], [0], None, [256], [0, 256])
        edge_hist = edge_hist.flatten()
        edge_hist = edge_hist / (edge_hist.sum() + 1e-7)
        
        # Combine all features
        encoding = np.concatenate([hist, np.array(regions), edge_hist])
        
        return encoding
    
    def encode_face_from_image(self, image_path):
        """
        Encode face from an image file using improved feature extraction.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            numpy.ndarray: Face encoding or None if no face found
        """
        try:
            # Read image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Detect faces
            faces = self.detect_face(image)
            
            if len(faces) == 0:
                return None  # No face detected
            
            if len(faces) > 1:
                return "multiple_faces"  # Multiple faces detected
            
            # Extract face region with some padding
            (x, y, w, h) = faces[0]
            # Add padding
            padding = 20
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)
            
            face_roi = image[y:y+h, x:x+w]
            
            # Convert to grayscale
            face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Create encoding
            encoding = self.create_face_encoding(face_gray)
            
            return encoding
            
        except Exception as e:
            print(f"Error encoding face: {e}")
            return None
    
    def save_encoding(self, encoding, roll_number):
        """
        Save face encoding to a file.
        
        Args:
            encoding (numpy.ndarray): Face encoding
            roll_number (str): Roll number to use as filename
            
        Returns:
            str: Path to saved encoding file or None
        """
        try:
            encoding_path = os.path.join(self.faces_dir, f"{roll_number}_encoding.pkl")
            with open(encoding_path, 'wb') as f:
                pickle.dump(encoding, f)
            return encoding_path
        except Exception as e:
            print(f"Error saving encoding: {e}")
            return None
    
    def load_encoding(self, encoding_path):
        """
        Load face encoding from a file.
        
        Args:
            encoding_path (str): Path to encoding file
            
        Returns:
            numpy.ndarray: Face encoding or None
        """
        try:
            with open(encoding_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading encoding: {e}")
            return None
    
    def recognize_face(self, face_encoding, known_encodings, tolerance=0.18):
        """
        Recognize a face by comparing with known encodings.
        
        Args:
            face_encoding (numpy.ndarray): Face encoding to recognize
            known_encodings (list): List of known face encodings
            tolerance (float): Recognition tolerance (lower = more strict, default 0.15)
            
        Returns:
            tuple: (match_index, distance) or (-1, float('inf')) if no match
        """
        try:
            if len(known_encodings) == 0:
                return -1, float('inf')
            
            # Calculate distances using cosine similarity
            best_match_index = -1
            best_distance = float('inf')
            
            for i, known_encoding in enumerate(known_encodings):
                # Check if shapes match
                if face_encoding.shape != known_encoding.shape:
                    # Try to match dimensions if possible
                    min_len = min(len(face_encoding), len(known_encoding))
                    face_enc = face_encoding[:min_len]
                    known_enc = known_encoding[:min_len]
                    # Print warning for debugging
                    if i == 0:  # Only print once
                        print(f"Warning: Encoding shape mismatch. Face: {face_encoding.shape}, Known: {known_encoding.shape}")
                else:
                    face_enc = face_encoding
                    known_enc = known_encoding
                
                # Normalize both encodings
                face_norm = face_enc / (np.linalg.norm(face_enc) + 1e-7)
                known_norm = known_enc / (np.linalg.norm(known_enc) + 1e-7)
                
                # Calculate cosine distance (1 - cosine similarity)
                cosine_distance = 1 - np.dot(face_norm, known_norm)
                
                # Also calculate normalized Euclidean distance
                euclidean_dist = np.linalg.norm(face_enc - known_enc)
                normalized_euclidean = euclidean_dist / (np.linalg.norm(face_enc) + np.linalg.norm(known_enc) + 1e-7)
                
                # Combined distance (weighted - more weight on cosine for histograms)
                combined_distance = 0.8 * cosine_distance + 0.2 * normalized_euclidean
                
                if combined_distance < best_distance:
                    best_distance = combined_distance
                    best_match_index = i
            
            # Check if best match is within tolerance (stricter now)
            if best_match_index != -1 and best_distance <= tolerance:
                return best_match_index, best_distance
            
            return -1, best_distance
        except Exception as e:
            print(f"Error recognizing face: {e}")
            return -1, float('inf')
    
    def load_all_encodings(self, encoding_paths):
        """
        Load all face encodings from file paths.
        
        Args:
            encoding_paths (list): List of encoding file paths
            
        Returns:
            list: List of face encodings
        """
        encodings = []
        for path in encoding_paths:
            encoding = self.load_encoding(path)
            if encoding is not None:
                encodings.append(encoding)
        return encodings
