"""
Helper utility functions
"""

import os
import sys
import darkdetect


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and PyInstaller

    Args:
        relative_path (str): Relative path to resource

    Returns:
        str: Absolute path to resource
    """
    if hasattr(sys, '_MEIPASS'):
        # Running in PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    # Running in normal Python environment
    return os.path.join(os.path.abspath("."), relative_path)


def get_theme():
    """
    Detect system theme (dark/light)

    Returns:
        str: 'dark' or 'light'
    """
    try:
        if darkdetect.isDark():
            return 'dark'
        return 'light'
    except Exception:
        # Default to light if detection fails
        return 'light'


def format_currency(amount):
    """
    Format number as Vietnamese currency

    Args:
        amount (int/float): Amount to format

    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return "0 ₫"
    return f"{int(amount):,} ₫".replace(',', '.')


def format_phone(phone):
    """
    Format phone number

    Args:
        phone (str): Phone number

    Returns:
        str: Formatted phone number
    """
    if not phone:
        return ""

    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))

    # Format as: 0XXX XXX XXX
    if len(digits) == 10:
        return f"{digits[:4]} {digits[4:7]} {digits[7:]}"

    return phone


def validate_email(email):
    """
    Simple email validation

    Args:
        email (str): Email address to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False

    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """
    Validate Vietnamese phone number

    Args:
        phone (str): Phone number to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not phone:
        return False

    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))

    # Vietnamese phone numbers are 10 digits starting with 0
    return len(digits) == 10 and digits[0] == '0'
