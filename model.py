import os
import pickle
import numpy as np
import cv2
import mediapipe as mp
from sklearn.neighbors import KNeighborsClassifier

MODEL_PATH = "face_model.clf"

# Correct MediaPipe initialization
mp_face_detection = mp.solutions.face_detection

def extract_embedding_for_image(image_stream):
    """
    Detects a face in the image stream and returns a dummy embedding 
    (flattened face image) for the KNN classifier.
    """
    # Convert image stream to numpy array
    file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    if image is None:
        return None

    # MediaPipe requires RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        results = face_detection.process(image_rgb)
        
        if not results.detections:
            return None
            
        # Get the first face
        detection = results.detections[0]
        bboxC = detection.location_data.relative_bounding_box
        ih, iw, _ = image.shape
        x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
        
        # Ensure box is within image bounds
        x, y = max(0, x), max(0, y)
        w, h = min(w, iw - x), min(h, ih - y)
        
        face_crop = image[y:y+h, x:x+w]
        
        if face_crop.size == 0:
            return None
            
        # Resize to fixed size for simple "embedding" (flattened pixels)
        # In a real production app, you would use FaceNet or InsightFace here.
        face_crop = cv2.resize(face_crop, (160, 160))
        return face_crop.flatten()

def train_model_background(dataset_dir, progress_callback):
    """
    Training loop that feeds progress back to the app.
    """
    X = []
    y = []
    
    student_ids = [d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))]
    total_students = len(student_ids)
    
    if total_students == 0:
        progress_callback(100, "No students found.")
        return

    for idx, student_id in enumerate(student_ids):
        student_folder = os.path.join(dataset_dir, student_id)
        images = os.listdir(student_folder)
        
        for img_name in images:
            img_path = os.path.join(student_folder, img_name)
            with open(img_path, "rb") as f:
                emb = extract_embedding_for_image(f)
                if emb is not None:
                    X.append(emb)
                    y.append(int(student_id))
        
        # Update progress
        percent = int(((idx + 1) / total_students) * 90)
        progress_callback(percent, f"Processed student {student_id}")

    if len(X) == 0:
        progress_callback(100, "No valid face images found.")
        return

    # Train KNN
    knn = KNeighborsClassifier(n_neighbors=1, metric='euclidean')
    knn.fit(X, y)
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(knn, f)
        
    progress_callback(100, "Training Complete!")

def load_model_if_exists():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    return None

def predict_with_model(clf, embedding):
    # Predict returns [label]
    label = clf.predict([embedding])[0]
    # Predict_proba returns [[prob_class1, prob_class2...]]
    # For KNN with k=1, probability is always 1.0, but we can simulate confidence
    # by distance if we used radius neighbors, but here we just return 1.0
    return label, 0.95