"""
Face Recognition System - Main Flask Application
A complete attendance system using face recognition technology.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from datetime import datetime
import csv
import io

from modules.database import Database
from modules.face_encoder import FaceEncoder
from modules.attendance_manager import AttendanceManager
from modules.camera import Camera

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'static/faces'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize modules
attendance_manager = AttendanceManager()
face_encoder = FaceEncoder()
camera = Camera()

# Global variable to store camera state
camera_active = False


def allowed_file(filename):
    """
    Check if file extension is allowed.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        bool: True if allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Homepage route."""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register face route."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        roll_number = request.form.get('roll_number', '').strip()
        
        # Validate inputs
        if not name or not roll_number:
            flash('Name and Roll Number are required!', 'error')
            return redirect(url_for('register'))
        
        # Check if file is uploaded
        if 'photo' not in request.files:
            flash('No photo uploaded!', 'error')
            return redirect(url_for('register'))
        
        file = request.files['photo']
        
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(url_for('register'))
        
        if not allowed_file(file.filename):
            flash('Invalid file type! Please upload PNG, JPG, or JPEG.', 'error')
            return redirect(url_for('register'))
        
        # Save uploaded file
        filename = secure_filename(f"{roll_number}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Register user
        result = attendance_manager.register_user(name, roll_number, filepath)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('register'))
        else:
            flash(result['message'], 'error')
            # Delete uploaded file if registration failed
            if os.path.exists(filepath):
                os.remove(filepath)
            return redirect(url_for('register'))
    
    return render_template('register.html')


@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    """Attendance page route."""
    return render_template('attendance.html')


@app.route('/start_camera', methods=['POST'])
def start_camera():
    """Start camera route."""
    global camera_active
    
    if camera.open_camera():
        camera_active = True
        return jsonify({'success': True, 'message': 'Camera started'})
    else:
        return jsonify({'success': False, 'message': 'Failed to open camera. Please check if camera is connected.'})


@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    """Stop camera route."""
    global camera_active
    camera.release_camera()
    camera_active = False
    return jsonify({'success': True, 'message': 'Camera stopped'})


@app.route('/capture_frame', methods=['POST'])
def capture_frame():
    """Capture frame and mark attendance route."""
    global camera_active
    
    if not camera_active or not camera.is_opened():
        return jsonify({'success': False, 'message': 'Camera is not active'})
    
    # Read frame from camera
    success, frame = camera.read_frame()
    
    if not success:
        return jsonify({'success': False, 'message': 'Failed to capture frame'})
    
    # Mark attendance (OpenCV frame is already in BGR format)
    result = attendance_manager.mark_attendance_from_frame(frame)
    
    return jsonify(result)


@app.route('/records')
def records():
    """Attendance records page route."""
    attendance_db = Database('database/attendance.db')
    records = attendance_db.get_attendance_records()
    return render_template('records.html', records=records)


@app.route('/manage_users')
def manage_users():
    """Manage users page - view and delete registered users."""
    users_db = Database('database/users.db')
    users = users_db.get_all_users()
    return render_template('manage_users.html', users=users)


@app.route('/delete_user/<roll_number>', methods=['POST'])
def delete_user(roll_number):
    """Delete user route."""
    import os
    
    users_db = Database('database/users.db')
    result = users_db.delete_user(roll_number)
    
    if result['success']:
        # Delete associated files
        try:
            if 'encoding_path' in result and result['encoding_path'] and os.path.exists(result['encoding_path']):
                os.remove(result['encoding_path'])
            if 'image_path' in result and result['image_path'] and os.path.exists(result['image_path']):
                os.remove(result['image_path'])
        except Exception as e:
            print(f"Error deleting files: {e}")
        
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('manage_users'))


@app.route('/export_csv')
def export_csv():
    """Export attendance records to CSV."""
    attendance_db = Database('database/attendance.db')
    records = attendance_db.get_attendance_records()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Name', 'Roll Number', 'Date', 'Time'])
    
    # Write records
    for record in records:
        writer.writerow([
            record['name'],
            record['roll_number'],
            record['date'],
            record['time']
        ])
    
    # Create response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'attendance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


@app.route('/video_feed')
def video_feed():
    """Video streaming route for live camera feed."""
    from flask import Response
    
    def generate_frames():
        """Generator function for video frames."""
        global camera_active
        
        while camera_active and camera.is_opened():
            success, frame = camera.read_frame()
            
            if not success:
                break
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            
            # Yield frame in multipart format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs('static/faces', exist_ok=True)
    os.makedirs('database', exist_ok=True)
    
    # Initialize databases
    Database('database/users.db')
    Database('database/attendance.db')
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

