from enum import Enum
from typing import Any, Optional

from pydantic import (
    BaseModel,
    ValidationInfo,
    computed_field,
    field_validator,
)

from .components import (
    Components,
)
from .json_schema import Item, PortType
from .utils import to_display_name


class Ext(str, Enum):
    TXT = "txt"
    CSV = "csv"
    PDF = "pdf"
    PNG = "png"
    JPEG = "jpeg"
    MPEG = "mpeg"
    WEBM = "webm"
    WAV = "wav"
    MP4 = "mp4"
    MP3 = "mp3"
    AVI = "avi"
    MKV = "mkv"
    MOV = "mov"
    WMV = "wmv"
    GIF = "gif"
    JPG = "jpg"
    TIFF = "tiff"
    TIF = "tif"
    BMP = "bmp"
    JP2 = "jp2"
    DIB = "dib"
    PGM = "pgm"
    PPM = "ppm"
    PNM = "pnm"
    RAS = "ras"
    HDR = "hdr"
    WEBP = "webp"


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


class Category(str, Enum):
    MODEL = "models"
    FUNCTION = "functions"
    API = "apis"
    UTILS = "utils"


class FieldMetadata(BaseModel):
    type: str
    name: str

    @computed_field
    @property
    def display_name(self) -> str:
        return to_display_name(self.name)

    description: Optional[str] = None
    default: Optional[Any] = None

    items: Optional[Item] = None

    @field_validator("items")
    @classmethod
    def check_items(cls, v: Optional[Item], info: ValidationInfo) -> Optional[Item]:
        if info.data.get("type") == PortType.ARRAY and v is None:
            raise ValueError("Items must be provided when type is ARRAY")
        return v

    show: bool
    required: bool

    component: Components


class MetaDataBase(BaseModel):
    @computed_field
    @property
    def image(self) -> str:
        return self.category.value + "/" + self.task + "/" + self.name

    name: str
    task: str
    description: str
    category: Category

    params: Optional[list[FieldMetadata]] = None
    inputs: Optional[list[FieldMetadata]] = None
    outputs: Optional[list[FieldMetadata]] = None


class FunctionMetaData(MetaDataBase):
    dockerfile_path: str
    docker_context: str


class ModelMetaData(FunctionMetaData):
    startup_params: Optional[list[FieldMetadata]] = None


class Method(str, Enum):
    get = "GET"
    post = "POST"
    patch = "PATCH"
    put = "PUT"
    delete = "DELETE"


class APIMetaData(MetaDataBase):
    pass


class UtilsMetaData(APIMetaData):
    pass


class StorageConfig(BaseModel):
    refresh_token: str
    access_token: str
    host: str

    @classmethod
    def configure(
        cls,
        refresh_token: str,
        access_token: str,
        host: str,
    ):
        cls.access_token = access_token
        cls.refresh_token = refresh_token
        cls.host = host


class CoreModel(BaseModel):
    pass
