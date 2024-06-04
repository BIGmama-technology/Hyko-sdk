import re
from typing import Any, Optional

from pydantic import Field

from .components.components import Components


def field(
    description: str,
    default: Optional[Any] = None,
    component: Optional[Components] = None,
    hidden: Optional[bool] = None,
    alias: Optional[str] = None,
) -> Any:
    return Field(
        default=default,
        description=description,
        alias=alias,
        json_schema_extra={
            "component": component.model_dump() if component else None,
            "hidden": hidden,
        },
    )


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


def to_image(image: str):
    """
    Remove any spaces, special characters, or numbers from a string and convert it to lowercase.

    Parameters:
    input_string (str): The string from which to remove special characters, spaces, and numbers.

    Returns:
    str: A new string containing only lowercase letters from the original string.
    """
    cleaned_image = image.replace(" ", "_")
    cleaned_image = re.sub(r"[^a-zA-Z/_]", "", image)
    cleaned_image = cleaned_image.lower()

    return cleaned_image
