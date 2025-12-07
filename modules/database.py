"""
Database Module
Handles all SQLite database operations for users and attendance records.
"""

import sqlite3
import os
from datetime import datetime


class Database:
    """Database class to manage SQLite operations."""
    
    def __init__(self, db_path):
        """
        Initialize database connection.
        
        Args:
            db_path (str): Path to the database file
        """
        self.db_path = db_path
        self.ensure_directory()
        self.init_database()
    
    def ensure_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def get_connection(self):
        """
        Get database connection.
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_number TEXT UNIQUE NOT NULL,
                face_encoding_path TEXT NOT NULL,
                image_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_number TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, name, roll_number, face_encoding_path, image_path):
        """
        Add a new user to the database.
        
        Args:
            name (str): User's name
            roll_number (str): User's roll number
            face_encoding_path (str): Path to face encoding file
            image_path (str): Path to user's image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, roll_number, face_encoding_path, image_path)
                VALUES (?, ?, ?, ?)
            ''', (name, roll_number, face_encoding_path, image_path))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
    
    def get_all_users(self):
        """
        Get all registered users.
        
        Returns:
            list: List of user dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name, roll_number, face_encoding_path, image_path FROM users')
        users = cursor.fetchall()
        conn.close()
        
        return [
            {
                'name': user[0],
                'roll_number': user[1],
                'face_encoding_path': user[2],
                'image_path': user[3]
            }
            for user in users
        ]
    
    def get_user_by_roll_number(self, roll_number):
        """
        Get user by roll number.
        
        Args:
            roll_number (str): Roll number to search for
            
        Returns:
            dict: User information or None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, roll_number, face_encoding_path, image_path 
            FROM users WHERE roll_number = ?
        ''', (roll_number,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'name': user[0],
                'roll_number': user[1],
                'face_encoding_path': user[2],
                'image_path': user[3]
            }
        return None
    
    def mark_attendance(self, name, roll_number):
        """
        Mark attendance for a user.
        
        Args:
            name (str): User's name
            roll_number (str): User's roll number
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = datetime.now()
            date = now.strftime('%Y-%m-%d')
            time = now.strftime('%H:%M:%S')
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if attendance already marked today
            cursor.execute('''
                SELECT id FROM attendance 
                WHERE roll_number = ? AND date = ?
            ''', (roll_number, date))
            
            if cursor.fetchone():
                conn.close()
                return False  # Already marked today
            
            # Mark attendance
            cursor.execute('''
                INSERT INTO attendance (name, roll_number, date, time)
                VALUES (?, ?, ?, ?)
            ''', (name, roll_number, date, time))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking attendance: {e}")
            return False
    
    def get_attendance_records(self):
        """
        Get all attendance records.
        
        Returns:
            list: List of attendance record dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, roll_number, date, time 
            FROM attendance 
            ORDER BY timestamp DESC
        ''')
        records = cursor.fetchall()
        conn.close()
        
        return [
            {
                'name': record[0],
                'roll_number': record[1],
                'date': record[2],
                'time': record[3]
            }
            for record in records
        ]
    
    def delete_user(self, roll_number):
        """
        Delete a user from the database.
        
        Args:
            roll_number (str): Roll number of user to delete
            
        Returns:
            dict: Result with success status and user info
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get user info before deleting
            cursor.execute('SELECT name, face_encoding_path, image_path FROM users WHERE roll_number = ?', (roll_number,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return {'success': False, 'message': 'User not found'}
            
            user_name, encoding_path, image_path = user
            
            # Delete user from database
            cursor.execute('DELETE FROM users WHERE roll_number = ?', (roll_number,))
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f'User {user_name} deleted successfully',
                'encoding_path': encoding_path,
                'image_path': image_path
            }
        except Exception as e:
            print(f"Error deleting user: {e}")
            return {'success': False, 'message': f'Error deleting user: {str(e)}'}

