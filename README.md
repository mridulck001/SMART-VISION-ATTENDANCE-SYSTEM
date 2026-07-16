# Smart Face Attendance System 🚀

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Flask-Web%20Framework-lightgrey.svg" alt="Flask">
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg" alt="OpenCV">
  <img src="https://img.shields.io/badge/MediaPipe-Face%20Detection-orange.svg" alt="MediaPipe">
  <img src="https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-yellow.svg" alt="Scikit-Learn">
</div>

<br>

A modern, highly interactive, and secure Face-Recognition Attendance System built with Python and modern web technologies. The system utilizes machine learning for accurate face detection and recognition, wrapped in a beautiful glassmorphic UI.

---

## 🌟 Key Features

### 📸 Seamless Face Recognition
- **Live Attendance:** Mark attendance directly from the browser using the device camera.
- **High Accuracy:** Powered by Google's MediaPipe for robust face detection and Scikit-learn (KNN) for reliable recognition.
- **Real-time Feedback:** Immediate visual feedback upon successful recognition.

### 🛡️ Secure Admin Workspace
- **Protected Routes:** All management functions are locked behind a secure session-based admin login.
- **Student Management:** Easily register new students, add their details, and capture training images directly through the web interface.
- **One-Click Training:** Train or retrain the machine learning model from the dashboard without touching the terminal.

### 📊 Data & Analytics
- **Dashboard Metrics:** View total students, attendance entries, and active training status at a glance.
- **Trend Charts:** Visualize attendance trends over the last 30 days.
- **Comprehensive Logs:** View, filter (daily/weekly/monthly), and export attendance records to CSV for integration with HR/School systems.
- **Local Storage:** Lightweight and fast SQLite database implementation for zero-config deployments.

### 🎨 Premium UI/UX
- **Modern Glassmorphism:** A stunning, unified dark theme with frosted glass panels, neon accents, and smooth micro-animations.
- **Responsive Design:** Fully optimized for both desktop and mobile viewports.

---

## 🚀 Quick Start

### Option 1: Run with Docker (Recommended)
The easiest way to get started is using Docker, which handles all dependencies for you.

```bash
# Build the image
docker build -t face-attendance .

# Run the container
docker run -p 7860:7860 face-attendance
```

### Option 2: Run Locally (Manual Setup)
Ensure you have Python 3.10+ installed.

```bash
# Clone the repository (if applicable)
# git clone <repo_url>
# cd face-recogniton-attendance-system

# Create a virtual environment (optional but recommended)
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The application will start on port `7860`. Visit `http://localhost:7860` in your browser.

---

## 🔐 Configuration & Defaults

By default, the application is configured with the following local admin credentials:
- **Username:** `admin`
- **Password:** `admin123`

*Note: For production deployments, it is highly recommended to change these credentials.*

---

## 🗺️ Project Navigation (Routes)

| Route | Description | Access Level |
|-------|-------------|--------------|
| `/` | Public landing page | Public |
| `/mark_attendance` | Live camera feed for marking attendance | Public |
| `/admin/login` | Admin authentication portal | Public |
| `/admin` | Main administrative dashboard | Admin Only |
| `/add_student` | Register new students and capture faces | Admin Only |
| `/attendance_record`| View and filter attendance history | Admin Only |
| `/download_csv` | Export records to a CSV file | Admin Only |
| `/students` | JSON API listing all students | Admin Only |
| `/students/<id>` | API endpoint to delete a student | Admin Only |

---

## 📁 Directory Structure

```text
face-recogniton-attendance-system/
├── app.py                  # Main Flask application & routes
├── model.py                # ML logic (training, prediction, MediaPipe wrap)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── attendance.db           # SQLite database (auto-generated)
├── face_model.clf          # Trained KNN model (auto-generated)
├── train_status.json       # Tracks current ML training status
├── dataset/                # Stores captured face images (auto-generated)
├── static/                 # Static assets
│   ├── css/style.css       # Global design system & glassmorphism
│   ├── js/                 # Frontend logic (camera, charts, dashboard)
│   └── images/             # Backgrounds & icons
└── templates/              # HTML views (Jinja2 templates)
    ├── index.html
    ├── admin_login.html
    ├── admin_dashboard.html
    ├── add_student.html
    ├── mark_attendance.html
    └── attendance_record.html
```

---

## 📚 Further Documentation

For more detailed information on how the system is architected and how you can contribute, please see the additional markdown files:

- [**ARCHITECTURE.md**](./ARCHITECTURE.md): Detailed explanation of the system components, data flow, and ML pipeline.
- [**CONTRIBUTING.md**](./CONTRIBUTING.md): Guidelines for contributing to the project, reporting bugs, and submitting pull requests.

---

## ⚠️ Notes & Troubleshooting
- **Camera Access:** The browser will request permission to access your webcam on the `/mark_attendance` and `/add_student` pages. Ensure you grant permission.
- **Port Conflicts:** If port `7860` is in use, modify `app.run(port=7860)` in `app.py` to an available port.
- **Model Training:** Initial recognition requires at least one registered student and a trained model. Add a student, capture their face, and click "Start Training" on the dashboard before attempting to mark attendance.
