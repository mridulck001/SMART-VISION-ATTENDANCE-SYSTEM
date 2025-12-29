FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install requirements FIRST
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir mediapipe==0.10.9
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# --- NEW TRICK: Delete any local mediapipe folder/file that was copied ---
RUN rm -rf /app/mediapipe /app/mediapipe.py

# Create dataset directory
RUN mkdir -p dataset && chmod 777 dataset

EXPOSE 7860

CMD ["python", "app.py"]