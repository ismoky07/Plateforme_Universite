"""
Utility helper functions
"""
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Optional


def get_directory_hash(directory_path: Path) -> str:
    """
    Generate a hash based on directory contents (file names + modification times)
    Used for cache invalidation
    """
    if not directory_path.exists():
        return ""

    hash_input = ""
    for file_path in sorted(directory_path.rglob("*")):
        if file_path.is_file():
            hash_input += f"{file_path.name}:{file_path.stat().st_mtime};"

    return hashlib.md5(hash_input.encode()).hexdigest()[:8]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system use
    """
    # Replace problematic characters
    replacements = {
        " ": "_",
        "/": "-",
        "\\": "-",
        ":": "-",
        "*": "",
        "?": "",
        '"': "",
        "<": "",
        ">": "",
        "|": ""
    }

    result = filename
    for old, new in replacements.items():
        result = result.replace(old, new)

    return result


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def calculate_weighted_average(grades: List[dict]) -> float:
    """
    Calculate weighted average from list of grade dictionaries
    """
    valid_grades = [
        g for g in grades
        if g.get("note") is not None and g.get("coefficient")
        and 0 <= g["note"] <= 20 and g["coefficient"] > 0
    ]

    if not valid_grades:
        return 0.0

    total_weighted = sum(g["note"] * g["coefficient"] for g in valid_grades)
    total_coef = sum(g["coefficient"] for g in valid_grades)

    return round(total_weighted / total_coef, 2) if total_coef > 0 else 0.0


def get_performance_level(percentage: float) -> str:
    """
    Get performance level description from percentage
    """
    if percentage >= 90:
        return "excellent"
    elif percentage >= 75:
        return "tres_bien"
    elif percentage >= 60:
        return "bien"
    elif percentage >= 50:
        return "assez_bien"
    elif percentage >= 40:
        return "passable"
    else:
        return "insuffisant"


def format_datetime(dt: Optional[datetime], format_str: str = "%d/%m/%Y %H:%M") -> str:
    """
    Format datetime object to string
    """
    if dt is None:
        return ""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt
    return dt.strftime(format_str)
