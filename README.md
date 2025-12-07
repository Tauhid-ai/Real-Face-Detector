# Face Recognition System

A complete automated attendance management system using face recognition technology. This project uses Python, Flask, OpenCV, and the face_recognition library to mark attendance by recognizing faces in real-time.

## 🎯 Features

- **User Registration**: Register users by uploading their photos with name and roll number
- **Face Encoding**: Automatic face encoding and storage using AI
- **Live Attendance**: Real-time face recognition using webcam
- **Attendance Records**: View all attendance records with date and time
- **CSV Export**: Export attendance records to CSV format
- **Modern UI**: Clean, responsive Bootstrap-based interface
- **Error Handling**: Comprehensive error handling for various scenarios

## 🛠️ Tech Stack

- **Python 3.x**
- **Flask** - Web framework
- **OpenCV** - Computer vision library (built-in face detection - no heavy dependencies!)
- **SQLite** - Database
- **Bootstrap 5** - Frontend framework
- **HTML/CSS/JavaScript** - Frontend technologies

**Note**: This project uses OpenCV's built-in face detection (Haar Cascades), so no need to install heavy libraries like dlib or face_recognition!

## 📁 Project Structure

```
Face-Recognition-System/
│── app.py                 # Main Flask application
│── requirements.txt       # Python dependencies
│── README.md             # Project documentation
│
├── static/
│   ├── faces/            # Stored registered face images
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/               # JavaScript files (if needed)
│
├── templates/
│   ├── index.html        # Homepage
│   ├── register.html     # User registration page
│   ├── attendance.html   # Attendance marking page
│   └── records.html      # Attendance records page
│
├── database/
│   ├── users.db          # Users database (auto-created)
│   └── attendance.db     # Attendance database (auto-created)
│
└── modules/
    ├── __init__.py       # Package initialization
    ├── database.py       # Database operations
    ├── face_encoder.py   # Face encoding/recognition
    ├── attendance_manager.py  # Attendance management
    └── camera.py         # Camera operations
```

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- Webcam (for attendance marking)
- pip (Python package manager)

### Step 1: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd Face-Recognition-System

# Or simply download and extract the project folder
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: All dependencies are lightweight and easy to install! No need for CMake or Visual C++ Build Tools.

### Step 4: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000` or `http://127.0.0.1:5000`

## 📖 Usage Guide

### 1. Register a New User

1. Navigate to **Register Face** from the homepage
2. Fill in the form:
   - Enter full name
   - Enter unique roll number
   - Upload a clear photo with one face visible
3. Click **Register Face**
4. Wait for success message

**Tips for best results:**
- Use clear, well-lit photos
- Ensure only one face is visible
- Face should be front-facing
- Avoid sunglasses or masks

### 2. Mark Attendance

1. Navigate to **Take Attendance**
2. Click **Start Camera** to activate webcam
3. Position yourself in front of the camera
4. Click **Mark Attendance**
5. Wait for recognition and confirmation
6. Click **Stop Camera** when done

**Note**: Each user can only mark attendance once per day.

### 3. View Attendance Records

1. Navigate to **Attendance Records**
2. View all attendance records in the table
3. Click **Export to CSV** to download records

## 🔧 Configuration

### Camera Settings

If your camera is not the default (index 0), you can modify the camera index in `modules/camera.py`:

```python
camera = Camera(camera_index=0)  # Change 0 to your camera index
```

### Face Recognition Tolerance

You can adjust the face recognition tolerance in `modules/face_encoder.py`:

```python
def recognize_face(self, face_encoding, known_encodings, tolerance=0.6):
    # Lower tolerance = more strict (default: 0.6)
```

## 🐛 Troubleshooting

### Camera Not Working

- Ensure your webcam is connected and not being used by another application
- Check camera permissions in your system settings
- Try changing the camera index in `modules/camera.py`

### Face Not Recognized

- Ensure the user is registered with a clear photo
- Check lighting conditions
- Make sure only one face is visible
- Try adjusting the tolerance value

### Installation Issues

If you encounter any issues:

**Windows:**
- Make sure Python 3.7+ is installed
- Use: `python -m pip install --upgrade pip` first

**Linux:**
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-dev
```

**Mac:**
```bash
brew install python3
```

### Database Errors

- Delete `database/users.db` and `database/attendance.db` to reset
- Ensure write permissions in the database directory

## 📝 API Endpoints

- `GET /` - Homepage
- `GET /register` - Registration page
- `POST /register` - Register new user
- `GET /attendance` - Attendance page
- `POST /start_camera` - Start camera
- `POST /stop_camera` - Stop camera
- `POST /capture_frame` - Mark attendance
- `GET /video_feed` - Video stream
- `GET /records` - Attendance records page
- `GET /export_csv` - Export records to CSV

## 🎨 Customization

### Changing Theme Colors

Edit `static/css/style.css` to customize colors:

```css
.bg-primary {
    background-color: #your-color !important;
}
```

### Modifying Database Schema

Edit `modules/database.py` to add new fields or tables.

## 🔒 Security Notes

- Change the `secret_key` in `app.py` for production
- Implement authentication for production use
- Validate and sanitize all user inputs
- Use HTTPS in production
- Secure file uploads

## 📄 License

This project is open source and available for educational purposes.

## 👨‍💻 Development

### Adding New Features

The project is modular, making it easy to extend:

1. **New Module**: Add to `modules/` directory
2. **New Route**: Add to `app.py`
3. **New Template**: Add to `templates/` directory

### Code Structure

- **Modular Design**: Each module handles a specific responsibility
- **OOP Principles**: Classes used for better organization
- **Error Handling**: Comprehensive error handling throughout
- **Comments**: Well-documented code for easy understanding

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please open an issue on the repository.

## 🙏 Acknowledgments

- Built with Flask
- Face recognition powered by face_recognition library
- UI designed with Bootstrap 5
- Icons from Bootstrap Icons

---

**Made with ❤️ for automated attendance management**
