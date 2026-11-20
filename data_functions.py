"""ArtMentor: локальное сохранение изображений, анализов и истории диалогов."""

import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
UPLOAD_DIR = DATA_DIR / "uploads"
DATA_FILE = DATA_DIR / "artmentor_history.json"


def _ensure_dirs():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> list:
    """Load saved analysis records. Returns an empty list if no history exists yet."""
    _ensure_dirs()
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_data(data: list) -> None:
    """Save all history records to JSON."""
    _ensure_dirs()
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def save_uploaded_image(image_bytes: bytes, original_name: str) -> str:
    """Save an uploaded image and return its relative path."""
    _ensure_dirs()
    suffix = Path(original_name or "artwork.png").suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        suffix = ".png"
    image_id = uuid.uuid4().hex
    image_path = UPLOAD_DIR / f"{image_id}{suffix}"
    image_path.write_bytes(image_bytes)
    return str(image_path)


def load_image(image_path: str) -> bytes | None:
    """Read an image saved by ArtMentor."""
    try:
        path = Path(image_path)
        if path.exists() and path.is_file():
            return path.read_bytes()
    except OSError:
        pass
    return None


def save_analysis(record: dict) -> dict:
    """Add a new analysis record to history."""
    records = load_data()
    record = dict(record)
    record.setdefault("id", uuid.uuid4().hex)
    record.setdefault("created_at", datetime.now().isoformat(timespec="seconds"))
    record.setdefault("conversation", [])
    records.insert(0, record)
    save_data(records)
    return record


def get_record(record_id: str) -> dict | None:
    for record in load_data():
        if record.get("id") == record_id:
            return record
    return None


def update_record(record_id: str, **updates) -> dict | None:
    records = load_data()
    for index, record in enumerate(records):
        if record.get("id") == record_id:
            record.update(updates)
            records[index] = record
            save_data(records)
            return record
    return None
