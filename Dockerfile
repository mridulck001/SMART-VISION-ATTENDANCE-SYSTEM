FROM python:3.10-slim

# Install modern system dependencies for MediaPipe and OpenCV
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Flask app files (since your app.py uses Flask)
COPY . .

# Ensure the dataset folder exists
RUN mkdir -p dataset && chmod 777 dataset

# Hugging Face Spaces port for Flask
EXPOSE 7860

# Run Flask on port 7860 and bind to 0.0.0.0
CMD ["python", "app.py"]