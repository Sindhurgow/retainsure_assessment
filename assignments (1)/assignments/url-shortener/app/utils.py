import re
import random
import string
from urllib.parse import urlparse
from typing import Optional

def is_valid_url(url: str) -> bool:
    """
    Validate if the provided string is a valid URL
    
    Args:
        url: The URL string to validate
        
    Returns:
        bool: True if valid URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    # Basic URL pattern validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False
    
    # Additional validation using urlparse
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False

def generate_short_code(length: int = 6) -> str:
    """
    Generate a random alphanumeric short code
    
    Args:
        length: Length of the short code (default: 6)
        
    Returns:
        str: Random alphanumeric string
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_unique_short_code(db_instance, length: int = 6, max_attempts: int = 10) -> Optional[str]:
    """
    Generate a unique short code that doesn't exist in the database
    
    Args:
        db_instance: Database instance to check for existing codes
        length: Length of the short code (default: 6)
        max_attempts: Maximum attempts to generate unique code (default: 10)
        
    Returns:
        Optional[str]: Unique short code or None if unable to generate
    """
    for _ in range(max_attempts):
        short_code = generate_short_code(length)
        
        # Check if code already exists
        existing_mapping = db_instance.get_url_mapping(short_code)
        if not existing_mapping:
            return short_code
    
    return None

def sanitize_url(url: str) -> str:
    """
    Sanitize URL by removing extra whitespace and ensuring proper format
    
    Args:
        url: The URL to sanitize
        
    Returns:
        str: Sanitized URL
    """
    if not url:
        return ""
    
    # Remove leading/trailing whitespace
    url = url.strip()
    
    # Add http:// if no scheme is provided
    if url and not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    return url

def validate_short_code(short_code: str) -> bool:
    """
    Validate if the short code format is correct
    
    Args:
        short_code: The short code to validate
        
    Returns:
        bool: True if valid format, False otherwise
    """
    if not short_code or not isinstance(short_code, str):
        return False
    
    # Check if it's exactly 6 characters and alphanumeric
    if len(short_code) != 6:
        return False
    
    # Check if it contains only alphanumeric characters
    return short_code.isalnum()