from typing import List, Optional
import hashlib
import logging

logger = logging.getLogger(__name__)


def calculate_secure_hash(data: str) -> str:
    """Calculates a secure SHA-256 hash of the input string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def append_to_list(item: str, target_list: Optional[List[str]] = None) -> List[str]:
    """Safely appends an item using an immutable default parameter."""
    if target_list is None:
        target_list = []
    target_list.append(item)
    return target_list


def read_file_safely(file_path: str) -> Optional[str]:
    """Reads a file with proper error handling and logging."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error reading {file_path}: {e}")
        return None
