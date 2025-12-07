"""
Attendance Manager Module
Handles attendance-related operations and face recognition for attendance marking.
"""

import os
import cv2
import numpy as np
from datetime import datetime
from modules.database import Database
from modules.face_encoder import FaceEncoder


class AttendanceManager:
    """Class to manage attendance operations."""
    
    def __init__(self, users_db_path='database/users.db', attendance_db_path='database/attendance.db'):
        """
        Initialize AttendanceManager.
        
        Args:
            users_db_path (str): Path to users database
            attendance_db_path (str): Path to attendance database
        """
        self.users_db = Database(users_db_path)
        self.attendance_db = Database(attendance_db_path)
        self.face_encoder = FaceEncoder()
    
    def register_user(self, name, roll_number, image_path):
        """
        Register a new user with face recognition.
        
        Args:
            name (str): User's name
            roll_number (str): User's roll number
            image_path (str): Path to user's image
            
        Returns:
            dict: Result dictionary with status and message
        """
        # Validate inputs
        if not name or not roll_number or not image_path:
            return {
                'success': False,
                'message': 'All fields are required'
            }
        
        # Check if user already exists
        existing_user = self.users_db.get_user_by_roll_number(roll_number)
        if existing_user:
            return {
                'success': False,
                'message': 'Roll number already registered'
            }
        
        # Encode face from image
        encoding = self.face_encoder.encode_face_from_image(image_path)
        
        if encoding is None:
            return {
                'success': False,
                'message': 'No face detected in the image. Please upload a clear face photo.'
            }
        
        # Check if multiple faces detected (encoding will be a string in this case)
        if isinstance(encoding, str) and encoding == "multiple_faces":
            return {
                'success': False,
                'message': 'Multiple faces detected. Please upload an image with only one face.'
            }
        
        # Save face encoding
        encoding_path = self.face_encoder.save_encoding(encoding, roll_number)
        
        if not encoding_path:
            return {
                'success': False,
                'message': 'Failed to save face encoding'
            }
        
        # Save user to database
        success = self.users_db.add_user(name, roll_number, encoding_path, image_path)
        
        if success:
            return {
                'success': True,
                'message': f'User {name} registered successfully!'
            }
        else:
            return {
                'success': False,
                'message': 'Failed to register user. Roll number may already exist.'
            }
    
    def mark_attendance_from_frame(self, frame):
        """
        Mark attendance by recognizing face from a video frame.
        
        Args:
            frame: Video frame (BGR format from OpenCV)
            
        Returns:
            dict: Result dictionary with status and user info
        """
        try:
            # Get all registered users
            users = self.users_db.get_all_users()
            
            if len(users) == 0:
                return {
                    'success': False,
                    'message': 'No users registered yet'
                }
            
            # Load all face encodings
            encoding_paths = [user['face_encoding_path'] for user in users]
            known_encodings = self.face_encoder.load_all_encodings(encoding_paths)
            
            if len(known_encodings) == 0:
                return {
                    'success': False,
                    'message': 'No face encodings found'
                }
            
            # Detect faces in frame
            faces = self.face_encoder.detect_face(frame)
            
            if len(faces) == 0:
                return {
                    'success': False,
                    'message': 'No face detected. Please position yourself in front of the camera.'
                }
            
            if len(faces) > 1:
                return {
                    'success': False,
                    'message': 'Multiple faces detected. Please ensure only one person is in frame.'
                }
            
            # Extract face region with padding (same as registration)
            (x, y, w, h) = faces[0]
            padding = 20
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(frame.shape[1] - x, w + 2 * padding)
            h = min(frame.shape[0] - y, h + 2 * padding)
            
            face_roi = frame[y:y+h, x:x+w]
            
            # Convert to grayscale
            face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Create encoding (same method as registration)
            face_encoding = self.face_encoder.create_face_encoding(face_gray)
            
            # Recognize face (returns index and distance)
            # Using slightly higher tolerance for better matching (0.18)
            match_index, match_distance = self.face_encoder.recognize_face(face_encoding, known_encodings, tolerance=0.18)
            
            if match_index == -1:
                # Face not recognized - provide helpful message
                # Find closest match for debugging
                closest_match = "Unknown"
                closest_roll = "N/A"
                if match_distance < float('inf') and match_distance < 0.5:  # Only show if somewhat close
                    # Find which user was closest (even if not close enough)
                    best_idx = -1
                    best_dist = float('inf')
                    for i, known_enc in enumerate(known_encodings):
                        if face_encoding.shape == known_enc.shape:
                            face_norm = face_encoding / (np.linalg.norm(face_encoding) + 1e-7)
                            known_norm = known_enc / (np.linalg.norm(known_enc) + 1e-7)
                            dist = 1 - np.dot(face_norm, known_norm)
                            if dist < best_dist:
                                best_dist = dist
                                best_idx = i
                    if best_idx != -1:
                        closest_match = users[best_idx]['name']
                        closest_roll = users[best_idx]['roll_number']
                
                if closest_match != "Unknown":
                    return {
                        'success': False,
                        'message': f'Face match nahi hua! Closest match: {closest_match} (Roll: {closest_roll}), Distance: {match_distance:.3f}. Kripya better lighting mein try karein ya dobara register karein.'
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Face database mein nahi mila! Kripya pehle register karein. (Distance: {match_distance:.3f})'
                    }
            
            # Get matched user
            matched_user = users[match_index]
            
            # Check if attendance already marked for this user today
            now = datetime.now()
            date = now.strftime('%Y-%m-%d')
            
            # Check attendance status
            attendance_db = Database('database/attendance.db')
            conn = attendance_db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, roll_number FROM attendance 
                WHERE roll_number = ? AND date = ?
            ''', (matched_user['roll_number'], date))
            existing = cursor.fetchone()
            conn.close()
            
            if existing:
                # Attendance already marked
                return {
                    'success': False,
                    'message': f'Attendance already marked today for {matched_user["name"]} (Roll: {matched_user["roll_number"]}). Aap aaj pehle hi attendance mark kar chuke hain.'
                }
            
            # Mark attendance
            success = self.attendance_db.mark_attendance(
                matched_user['name'],
                matched_user['roll_number']
            )
            
            if success:
                return {
                    'success': True,
                    'message': f'Attendance marked successfully for {matched_user["name"]} (Roll: {matched_user["roll_number"]})!',
                    'user': matched_user
                }
            else:
                return {
                    'success': False,
                    'message': f'Error marking attendance for {matched_user["name"]}. Please try again.'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
