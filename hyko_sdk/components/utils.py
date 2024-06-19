import re


def to_display_name(field_name: str) -> str:
    """
    Converts a Python variable name into a human-readable display name.

    Parameters:
    - field_name (str): The original variable name to be transformed.

    Returns:
    - str: A string that is more readable and suitable for user interfaces

    Example:
    to_display_name("userAge_dataInput")
    'User Age Data Input'
    """
    # Remove any special characters except underscores
    cleaned_name = re.sub(r"[^a-zA-Z0-9_ ]", "", field_name)

    # Replace underscores with spaces
    spaced_name = cleaned_name.replace("_", " ")

    # Convert camel case to spaces
    readable_name = re.sub(r"(?<!^)(?=[A-Z])", " ", spaced_name).title()

    return readable_name
