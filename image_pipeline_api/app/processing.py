import os, time, json
from datetime import datetime
from PIL import Image, ExifTags
from .db import update_image, get_image
from .ai import caption_image
from .logger import logger

THUMB_SIZES = {"small": (128,128), "medium": (512,512)}

def _exif(img):
    out = {}
    try:
        raw = img._getexif()
        if raw:
            for k,v in raw.items():
                tag = ExifTags.TAGS.get(k, k)
                if isinstance(v, bytes):
                    try: v = v.decode(errors="ignore")
                    except: v = str(v)
                out[str(tag)] = v
    except Exception as e:
        logger.warning(f"EXIF read failed: {e}")
    return out

def process_image(image_id: str):
    logger.info(f"processing {image_id}")
    t0 = time.time()
    rec = get_image(image_id)
    orig = rec["stored_path"]
    try:
        with Image.open(orig) as im:
            im = im.convert("RGB")
            w, h = im.width, im.height
            im.save(orig, format="JPEG", quality=95)
            base = os.path.dirname(orig)
            small  = os.path.join(base, "thumb_small.jpg")
            medium = os.path.join(base, "thumb_medium.jpg")

            for name, size in THUMB_SIZES.items():
                th = im.copy(); th.thumbnail(size)
                th.save(small if name=="small" else medium, format="JPEG", quality=90)

            size_bytes = os.path.getsize(orig)
            exif = _exif(im)
            caption = caption_image(orig)

            update_image(image_id, {
              "width": w, "height": h, "format": "jpg",
              "size_bytes": size_bytes,
              "exif_json": json.dumps(exif) if exif else None,
              "thumb_small_path": small, "thumb_medium_path": medium,
              "caption": caption,
              "processed_at": datetime.utcnow().isoformat()+"Z",
              "status": "success",
              "processing_time_ms": int((time.time()-t0)*1000),
              "error": None
            })
    except Exception as e:
        logger.exception("processing failed")
        update_image(image_id, {
          "status":"failed", "error":str(e),
          "processing_time_ms": int((time.time()-t0)*1000)
        })
