# Use a stable Python version
FROM python:3.10-slim

# Install system dependencies for MediaPipe and OpenCV
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directory for datasets and set permissions
RUN mkdir -p dataset && chmod 777 dataset

# Expose Streamlit's default port
EXPOSE 8501

# Run with XSRF protection disabled to prevent 403 errors on Hugging Face
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]