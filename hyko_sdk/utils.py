import re
from typing import Any, Optional

from pydantic import Field

from hyko_sdk.components import Components


def field(
    description: str,
    default: Optional[Any] = None,
    show: bool = True,
    required: bool = True,
    component: Optional[Components] = None,
) -> Any:
    return Field(
        default=default,
        description=description,
        json_schema_extra={
            "show": show,
            "required": required,
            "component": component.model_dump() if component else None,
        },
    )


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
    cleaned_name = re.sub(r"[^a-zA-Z0-9_]", "", field_name)

    # Replace underscores with spaces
    spaced_name = cleaned_name.replace("_", " ")

    # Convert camel case to spaces
    readable_name = re.sub(r"(?<!^)(?=[A-Z])", " ", spaced_name).title()

    return readable_name


mimetype_to_extension = {
    "text/plain": "txt",
    "text/csv": "csv",
    "application/pdf": "pdf",
    "image/png": "png",
    "image/jpeg": "jpeg",
    "image/gif": "gif",
    "image/bmp": "bmp",
    "image/webp": "webp",
    "audio/wav": "wav",
    "audio/mpeg": "mp3",
    "video/mp4": "mp4",
    "video/vnd.avi": "avi",
    "video/webm": "webm",
    "video/mpeg": "mpeg",
    "video/x-matroska": "mkv",
    "video/quicktime": "mov",
    "video/x-ms-wmv": "wmv",
}
extension_to_mimetype = {value: key for key, value in mimetype_to_extension.items()}
