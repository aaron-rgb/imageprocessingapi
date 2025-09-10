# imageprocessingapi
# Project Overview
# This Project implements an Image Processing Pipelien.
# The API allows users to:
  1) Upload images (JPG/PNG)
  2) Generate thumbnails (small = 128px, medium = 512px)
  3) Extract metadata and EXIF data
  4) Generate AI captions using Huggign Face BLIP
  5) Store all results in a SQLite database
  6) Expose REST endpoints to list images, view details, download thumbnails, and get statistics.

# Installation Steps
Option 1 : Run with Docker (recommended)
1) Build the docker image:
   docker build -t image-pipeline .
2) Run the container:
   docker run --rm -p 8000:8000 --name image-pipeline image-pipeline
3) (Optional) Persist files on host:
  docker run --rm -p 8000:8000 ` -v "${PWD}\storage:/app/storage" ` -v "${PWD}\logs:/app/logs" ` -v "${PWD}\data.db:/app/data.db" ` --name image-pipeline ` image-pipeline

Option 2: Run locally
1) Create virtual environment and install dependencies:
   python -m venv .venv
  .venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  pip install transformers torch torchvision
2) Start the server:
   uvicorn app.main:app --reload

# API Documentation
