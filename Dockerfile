FROM python:3.10-slim

# Install system dependencies for MediaPipe
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files (including static/ and templates/)
COPY . .

# Ensure data directories are writable
RUN mkdir -p dataset && chmod 777 dataset

# Hugging Face MUST use port 7860
EXPOSE 7860

# Run the app
CMD ["python", "app.py"]