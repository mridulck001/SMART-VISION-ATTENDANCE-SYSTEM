# System Architecture

The Smart Face Attendance System is designed as a monolithic web application utilizing a Model-View-Controller (MVC) pattern, implemented via Flask. It bridges traditional web routing with real-time computer vision capabilities in the browser.

## High-Level Architecture

The system consists of three main layers:

1. **Frontend (Client-Side)**
   - **UI:** Built with HTML5, Bootstrap 5, and a custom CSS design system leveraging modern "glassmorphism".
   - **Logic:** Vanilla JavaScript manages DOM interactions, Chart.js for data visualization, and the HTML5 `navigator.mediaDevices.getUserMedia` API for accessing the webcam directly in the browser.
   - **Video Streaming:** The frontend captures video frames, but instead of sending raw heavy video to the server, it captures snapshot frames (base64 encoded JPEGs) and sends them to the backend via REST API endpoints for processing during the "Add Student" and "Mark Attendance" phases.

2. **Backend (Server-Side - Flask)**
   - **Routing & Auth:** Flask handles route definitions, template rendering (Jinja2), and session-based authentication for the admin area.
   - **Business Logic:** Orchestrates the flow between database operations, file storage (for the face dataset), and the Machine Learning model.

3. **Machine Learning Pipeline (Computer Vision)**
   - **Detection:** `MediaPipe Face Detection` is used to rapidly and accurately locate faces within the frames sent from the client.
   - **Extraction & Embedding:** `OpenCV` (cv2) processes the image matrices, cropping and resizing the detected faces.
   - **Classification:** A K-Nearest Neighbors (KNN) classifier from `scikit-learn` is trained on flattened image arrays. When marking attendance, the classifier matches incoming faces against the trained dataset.

## Data Flow

### 1. Adding a Student (Data Collection)
1. Admin fills out student details (Name, Roll, Reg No).
2. The browser requests webcam access and streams video to a `<video>` element.
3. JavaScript captures 50 individual frames and POSTs them to the backend.
4. Backend uses MediaPipe to verify a face exists, crops it, and saves it to `dataset/[Name]_[Roll]/`.
5. Student details are saved to the SQLite database.

### 2. Model Training
1. Admin triggers training via the dashboard.
2. The backend iterates through the `dataset/` directory.
3. Images are flattened into 1D arrays (features) and associated with their folder names (labels).
4. The KNN model is trained on these features and serialized to disk as `face_model.clf` (using `joblib`).

### 3. Marking Attendance (Inference)
1. The user opens the public scanner.
2. The browser continuously captures frames and POSTs them to the recognition endpoint.
3. Backend detects the face using MediaPipe, extracts it, and passes it to the loaded `face_model.clf`.
4. The model predicts the identity.
5. If identified with high confidence, an attendance record is inserted into the SQLite database with the current UTC timestamp.

## Database Schema (SQLite)

The system uses a lightweight SQLite database (`attendance.db`) with the following core tables (conceptual):

- **Students Table:** Stores `id`, `name`, `roll`, `reg_no`, `class`, `section`.
- **Attendance Table:** Stores `id`, `student_id`, `name`, `timestamp`.

## Security Considerations
- **Admin Access:** Protected by standard Flask session cookies. Secret keys should be securely managed in production via environment variables.
- **Data Privacy:** Face images are stored locally on the server. No biometric data is sent to external APIs.
