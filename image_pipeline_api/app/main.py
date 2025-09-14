# app/main.py
import os, uuid
from datetime import datetime
from typing import Literal

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db, insert_image, get_image, list_images, get_stats
from .processing import process_image
from .logger import logger  # uses explicit handlers in app/logger.py

ALLOWED = {"image/jpeg", "image/jpg", "image/png"}

app = FastAPI(title="Image Processing Pipeline API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    os.makedirs("storage", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    logger.info("Startup complete: DB initialized and directories ensured (storage/, logs/).")


@app.post("/api/images")
async def upload(background: BackgroundTasks, file: UploadFile = File(...)):
    # Validate
    if file.content_type not in ALLOWED:
        logger.warning(f"Rejected upload: filename={file.filename!r}, content_type={file.content_type!r}")
        raise HTTPException(400, "Unsupported file type. Use JPG or PNG.")

    # Prepare storage
    image_id = str(uuid.uuid4())
    img_dir = os.path.join("storage", image_id)
    os.makedirs(img_dir, exist_ok=True)
    original_path = os.path.join(img_dir, "original.jpg")
    logger.info(f"Received upload: id={image_id}, name={file.filename!r}, ct={file.content_type!r}")

    # Save original
    data = await file.read()
    with open(original_path, "wb") as f:
        f.write(data)
    logger.info(f"Saved original image: id={image_id}, path={original_path}")

    # Insert DB record (status=processing)
    insert_image({
        "id": image_id,
        "original_name": file.filename,
        "content_type": file.content_type,
        "stored_path": original_path,
        "size_bytes": None,
        "width": None, "height": None, "format": None,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "processed_at": None,
        "status": "processing",
        "caption": None,
        "exif_json": None,
        "thumb_small_path": None,
        "thumb_medium_path": None,
        "error": None,
        "processing_time_ms": None,
    })
    logger.info(f"DB insert complete: id={image_id}, status=processing")

    # Non-blocking processing (bonus)
    background.add_task(process_image, image_id)
    logger.info(f"Queued background processing: id={image_id}")

    base = os.getenv("BASE_URL", "http://localhost:8000")
    return JSONResponse({
        "status": "queued",
        "data": {
            "image_id": image_id,
            "original_name": file.filename,
            "processed_at": None,
            "metadata": None,
            "thumbnails": {
                "small":  f"{base}/api/images/{image_id}/thumbnails/small",
                "medium": f"{base}/api/images/{image_id}/thumbnails/medium",
            },
        },
        "error": None,
    })


@app.get("/api/images")
def list_all():
    base = os.getenv("BASE_URL", "http://localhost:8000")
    rows = list_images()
    logger.info(f"Listing images: count={len(rows)}")
    return {
        "status": "success",
        "data": [{
            "image_id": r["id"],
            "original_name": r["original_name"],
            "status": r["status"],
            "processed_at": r["processed_at"],
            "thumbnails": {
                "small":  f"{base}/api/images/{r['id']}/thumbnails/small",
                "medium": f"{base}/api/images/{r['id']}/thumbnails/medium",
            },
        } for r in rows],
        "error": None,
    }


@app.get("/api/images/{image_id}")
def details(image_id: str):
    rec = get_image(image_id)
    if not rec:
        logger.warning(f"Details requested for missing id={image_id}")
        raise HTTPException(404, "Image not found")

    base = os.getenv("BASE_URL", "http://localhost:8000")
    meta = None
    if rec["width"] and rec["height"]:
        meta = {
            "width": rec["width"],
            "height": rec["height"],
            "format": rec["format"],
            "size_bytes": rec["size_bytes"],
        }
    logger.info(f"Details served: id={image_id}, status={rec['status']}")
    return {
        "status": "success",
        "data": {
            "image_id": rec["id"],
            "original_name": rec["original_name"],
            "processed_at": rec["processed_at"],
            "status": rec["status"],
            "metadata": meta,
            "caption": rec["caption"],
            "exif": rec["exif_json"],
            "thumbnails": {
                "small":  f"{base}/api/images/{image_id}/thumbnails/small",
                "medium": f"{base}/api/images/{image_id}/thumbnails/medium",
            },
        },
        "error": rec["error"],
    }


@app.get("/api/images/{image_id}/thumbnails/{size}")
def thumb(image_id: str, size: Literal["small", "medium"]):
    rec = get_image(image_id)
    if not rec:
        logger.warning(f"Thumbnail requested for missing id={image_id}, size={size}")
        raise HTTPException(404, "Image not found")

    path = rec["thumb_small_path"] if size == "small" else rec["thumb_medium_path"]
    if not path or not os.path.exists(path):
        logger.warning(f"Thumbnail not ready/missing: id={image_id}, size={size}, path={path}")
        raise HTTPException(404, "Thumbnail not ready or missing")

    logger.info(f"Thumbnail served: id={image_id}, size={size}, path={path}")
    return FileResponse(path, media_type="image/jpeg")


@app.get("/api/stats")
def stats():
    s = get_stats()
    logger.info(f"Stats served: total={s.get('total')}, success={s.get('success')}, failed={s.get('failed')}")
    return {"status": "success", "data": s, "error": None}
