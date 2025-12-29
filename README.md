---
title: Smart Face Recognition Attendance System
emoji: 📸
colorFrom: green
colorTo: blue
sdk: docker
pinned: true
app_port: 7860
---

# 📸 Smart Face Recognition Attendance System

A robust, web-based application that automates student attendance using facial recognition technology. Built with **Flask**, **OpenCV**, **MediaPipe**, and **Scikit-learn**, this system allows for real-time recognition, seamless student management, and automated record-keeping.

## 🚀 Live Demo
Check out the running application here on Hugging Face Spaces!
*(If this is hosted on a Space, the "Open in App" button above will work automatically)*

---

## ✨ Key Features

* **🎓 Student Management**: easily add new students with details like Roll Number, Class, and Section.
* **📸 In-Browser Data Collection**: Capture face datasets directly from the webcam within the browser.
* **🧠 Fast Training**: Uses **MediaPipe** for face detection and **KNN (K-Nearest Neighbors)** for recognition, ensuring quick training on CPU environments.
* **⏱️ Real-Time Attendance**: Recognizes faces instantly and marks attendance with a timestamp.
* **📊 Dashboard & Analytics**: View attendance logs filtered by Daily, Weekly, or Monthly views.
* **💾 Export Data**: Download attendance records as `.csv` files for external use.
* **🔒 Privacy First**: All data is stored locally in a SQLite database; no external cloud APIs are used.

---

## 🛠️ Tech Stack

* **Backend**: Python, Flask
* **Computer Vision**: OpenCV, MediaPipe (Google)
* **Machine Learning**: Scikit-learn (KNN Classifier)
* **Database**: SQLite
* **Frontend**: HTML5, Bootstrap, JavaScript
* **Deployment**: Docker

---

## ⚙️ Installation & Usage

### Option 1: Run via Docker (Recommended)

This ensures all dependencies (especially MediaPipe) are installed correctly.

```bash
# 1. Build the image
docker build -t face-attendance .

# 2. Run the container (Access at http://localhost:7860)
docker run -p 7860:7860 face-attendance

```

### Option 2: Run Locally (Python)

Ensure you have Python 3.10+ installed.

```bash
# 1. Clone the repository
git clone [https://huggingface.co/spaces/YOUR_USERNAME/face-recognition-attendance](https://huggingface.co/spaces/YOUR_USERNAME/face-recognition-attendance)
cd face-recognition-attendance

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py

```

---

## 📖 How to Use

1. **Add Student**: Go to the "Add Student" page. Enter details and click "Save".
2. **Capture Photos**: The camera will open. Click "Capture" multiple times to save face samples (20-50 images recommended).
3. **Train Model**: Go to the Home page and click **"Train Model"**. Wait for the progress bar to reach 100%.
4. **Mark Attendance**: Go to the "Mark Attendance" page. The camera will scan for faces. When a student is recognized, their name and confidence score will appear, and attendance is saved.
5. **View Records**: Check the "Attendance Records" page to see the logs or download the CSV.

---

## 📂 Project Structure

```
├── app.py                 # Main Flask application entry point
├── model.py               # ML logic (MediaPipe extraction + KNN training)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── attendance.db          # SQLite database (auto-created)
├── train_status.json      # Training progress tracker
├── static/                # CSS, JS, and images
├── templates/             # HTML files
└── dataset/               # Stores raw face images (auto-created)

```

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📄 License

This project is open-source and available under the MIT License.