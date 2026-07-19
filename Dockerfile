FROM python:3.12-slim

# Library sistem yang dibutuhkan untuk compile dlib (face_recognition)
# dan untuk opencv-python-headless bisa baca/tulis gambar.
RUN apt-get update && apt-get install -y --no-install-recommends \
    cmake \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-render.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render otomatis meng-inject env var PORT saat runtime.
EXPOSE 10000

CMD gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
