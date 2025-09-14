import sqlite3
from contextlib import contextmanager

DB_PATH = "data.db"

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS images (
          id TEXT PRIMARY KEY,
          original_name TEXT, content_type TEXT, stored_path TEXT,
          size_bytes INTEGER, width INTEGER, height INTEGER, format TEXT,
          created_at TEXT, processed_at TEXT, status TEXT,
          caption TEXT, exif_json TEXT,
          thumb_small_path TEXT, thumb_medium_path TEXT,
          error TEXT, processing_time_ms INTEGER
        )""")
        c.commit()

@contextmanager
def conn():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    try: yield con
    finally: con.close()

def insert_image(rec: dict):
    with conn() as c:
        cols = ",".join(rec.keys())
        c.execute(f"INSERT INTO images ({cols}) VALUES ({','.join(['?']*len(rec))})", list(rec.values()))
        c.commit()

def update_image(id_, updates: dict):
    with conn() as c:
        sets = ",".join([f"{k}=?" for k in updates])
        c.execute(f"UPDATE images SET {sets} WHERE id=?", list(updates.values())+[id_])
        c.commit()

def get_image(id_):
    with conn() as c:
        r = c.execute("SELECT * FROM images WHERE id=?", (id_,)).fetchone()
        return dict(r) if r else None

def list_images():
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM images ORDER BY created_at DESC").fetchall()]

def get_stats():
    with conn() as c:
        total   = c.execute("SELECT COUNT(*) FROM images").fetchone()[0]
        success = c.execute("SELECT COUNT(*) FROM images WHERE status='success'").fetchone()[0]
        failed  = c.execute("SELECT COUNT(*) FROM images WHERE status='failed'").fetchone()[0]
        avg     = c.execute("SELECT AVG(processing_time_ms) FROM images WHERE status='success'").fetchone()[0]
        return {
          "total": total, "success": success, "failed": failed,
          "success_rate": (success/total) if total else 0.0,
          "failure_rate": (failed/total) if total else 0.0,
          "avg_processing_time_ms": float(avg) if avg is not None else None
        }
