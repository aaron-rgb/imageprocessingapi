FROM python:3.11-slim

WORKDIR /app

# System deps for Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    gcc \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# enable AI captioning:
 RUN pip install --no-cache-dir transformers torch torchvision

COPY . .

EXPOSE 8000
ENV BASE_URL=http://localhost:8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
