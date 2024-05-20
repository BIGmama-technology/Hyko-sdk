from typing import Any, Optional

from pydantic import Field

from .components.components import Components


def field(
    description: str,
    default: Optional[Any] = None,
    component: Optional[Components] = None,
) -> Any:
    return Field(
        default=default,
        description=description,
        json_schema_extra={
            "component": component.model_dump() if component else None,
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
