# app/logger.py
import logging, os

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("image-pipeline")
logger.setLevel(logging.INFO)
logger.propagate = False  # don't double-log via root/uvicorn

# attach once
if not logger.handlers:
    fh = logging.FileHandler("logs/app.log", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(sh)
