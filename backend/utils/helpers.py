import uuid
import os

def generate_report_id() -> str:
    """Generate a unique random ID for reports."""
    return str(uuid.uuid4())

def ensure_dir(path: str):
    """Ensure a directory exists."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
