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
   Note: This runs fully inside the container with no host mounts, Data persists while the container is running.


# API Documentation
# 1) POST /api/images
   Upload an image (JPG/PNG). Processing runs in the background; response returns a queued status and thumbnail URLs.
   Request (curl): curl -X POST "http://localhost:8000/api/images" -F "file=@test.jpg"
  Response: 
  {
    "status": "queued",
    "data": {
      "image_id": "a1b2c3d4-...",
      "original_name": "test.jpg",
      "processed_at": null,
      "metadata": null,
      "thumbnails": {
        "small": "http://localhost:8000/api/images/a1b2c3d4.../thumbnails/small",
        "medium":"http://localhost:8000/api/images/a1b2c3d4.../thumbnails/medium"
      }
    },
    "error": null
  }
  Errors:
  { "status":"error","data":null,"error":"Unsupported file type. Use JPG or PNG." }

# 2) GET /api/images
List all images (processed or processing).
Request(curl): curl http://localhost:8000/api/images
Response:
{
  "status": "success",
  "data":[
    {
      "image_id": "a1b2c3d4-...",
      "original_name": "test.jpg",
      "status": "success",
      "processed_at": "2025-09-14T12:00:00Z",
      "thumbnails": {
        "small": "http://localhost:8000/api/images/a1b2c3d4.../thumbnails/small",
        "medium":"http://localhost:8000/api/images/a1b2c3d4.../thumbnails/medium"
      }
    }
  "error": null
}
# 3) GET /api/images/{id}
Get metdata, caption, EXIF, and thumbnail URLs for a specific image.
Request (curl): curl "http://localhost:8000/api/images/<image_id>"
Response:
{
  "status": "success",
  "data": {
    "image_id": "a1b2c3d4-...",
    "original_name": "test.jpg",
    "processed_at": "2025-09-14T12:00:00Z",
    "status": "success",
    "metadata": { "width": 1920, "height": 1080, "format": "jpg", "size_bytes": 2048576 },
    "caption": "A small dog playing in the grass",
    "exif": "{\"Make\": \"Apple\", \"Model\": \"iPhone\"}",
    "thumbnails": {
      "small": "http://localhost:8000/api/images/a1b2c3d4.../thumbnails/small",
      "medium":"http://localhost:8000/api/images/a1b2c3d4.../thumbnails/medium"
    }
  },
  "error": null
}
Error:
{ "status":"error","data":null,"error":"Image not found" }
# 4) GET /api/images/{id}/thumbnails/{small|medium}

Request (curl):
curl -o thumb_small.jpg "http://localhost:8000/api/images/<image_id>/thumbnails/small"
curl -o thumb_medium.jpg "http://localhost:8000/api/images/<image_id>/thumbnails/medium"
Error:
{ "status":"error","data":null,"error":"Thumbnail not ready or missing" }

# 5) GET /api/stats
Aggregate processing statistics.
Request (curl): curl http://localhost:8000/api/stats
Response:
{
  "status": "success",
  "data": {
    "total": 5,
    "success": 5,
    "failed": 0,
    "success_rate": 1.0,
    "failure_rate": 0.0,
    "avg_processing_time_ms": 1234.5
  },
  "error": null
}
Error:
{
  "status": "error",
  "data": null,
  "error": "Descriptive message"
}

**Workflow Example**
# 1) Upload an image
curl -X POST "http://localhost:8000/api/images" -F "file=@test.jpg"

# 2) List all images
curl http://localhost:8000/api/images

# 3) Get details (replace <id>)
curl "http://localhost:8000/api/images/<id>"

# 4) Download thumbnails
curl -o thumb_small.jpg  "http://localhost:8000/api/images/<id>/thumbnails/small"
curl -o thumb_medium.jpg "http://localhost:8000/api/images/<id>/thumbnails/medium"

# 5) View stats
curl http://localhost:8000/api/stats

**Optional (To show that the records are in the DB while the container is running)**
docker exec -it image-pipeline python - <<'PY'
import sqlite3, json
con = sqlite3.connect("/app/data.db")
rows = con.execute("SELECT id, original_name, status, created_at FROM images ORDER BY created_at DESC LIMIT 5").fetchall()
print(json.dumps([{"id":r[0],"name":r[1],"status":r[2],"created_at":r[3]} for r in rows], indent=2))
PY

**Logging**
# console logs
docker logs -f image-pipeline
# file logs inside the container
docker exec -it image-pipeline sh -c "tail -n 100 /app/logs/app.log"

