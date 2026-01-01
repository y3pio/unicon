"""Date utilities"""
import re
from datetime import datetime


def validate_date(date_str):
    """
    Validate and parse date string in YYYY-MM-DDTHH:MM:SSZ format
    
    Args:
        date_str: Date string to validate
    
    Returns:
        Validated date string
    
    Raises:
        ValueError: If date format is invalid
    """
    if not date_str:
        return None
    
    # Check format: YYYY-MM-DDTHH:MM:SSZ
    date_regex = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    if not re.match(date_regex, date_str):
        raise ValueError(
            f"Invalid date format. Expected YYYY-MM-DDTHH:MM:SSZ (e.g., 2024-01-01T00:00:00Z), got: {date_str}"
        )
    
    # Validate it's a valid date
    try:
        datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"Invalid date: {date_str}")
    
    return date_str

