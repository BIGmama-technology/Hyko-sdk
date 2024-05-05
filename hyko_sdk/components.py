from enum import Enum
from typing import Annotated, Any, Optional, Union

from pydantic import BaseModel, Discriminator, Tag, computed_field


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


class PortType(str, Enum):
    BOOLEAN = "boolean"
    NUMBER = "number"
    INTEGER = "integer"
    STRING = "string"
    ARRAY = "array"

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    PDF = "pdf"

    ANY = "any"
    OBJECT = "object"


class Component(BaseModel):
    @computed_field
    @property
    def name(self) -> str:
        return self.__class__.__name__


class Blank(Component):
    pass


class Slider(Component):
    leq: int
    geq: int
    step: float = 1


class Toggle(Component):
    pass


class Select(Component):
    choices: list[str | int | float]


class TextField(Component):
    placeholder: str
    multiline: bool = False
    secret: bool = False


class NumberField(Component):
    placeholder: str


class SubField(BaseModel):
    type: str
    name: str
    description: str

    component: "Components"


class StorageSelect(Component):
    supported_ext: list[Ext]


class ImagePreview(Component):
    placeholder: str


class ComplexComponent(Component):
    fields: list[SubField]


class ListComponent(Component):
    item_component: "Components"


def get_name(v: Any):
    """Name discriminator function."""
    try:
        return v.get("name")
    except Exception:
        return v.name


Components = Annotated[
    Union[
        Annotated[Toggle, Tag("Toggle")],
        Annotated[Select, Tag("Select")],
        Annotated[Slider, Tag("Slider")],
        Annotated[TextField, Tag("TextField")],
        Annotated[NumberField, Tag("NumberField")],
        Annotated[ComplexComponent, Tag("ComplexComponent")],
        Annotated[Blank, Tag("Blank")],
        Annotated[ListComponent, Tag("ListComponent")],
        Annotated[StorageSelect, Tag("StorageSelect")],
        Annotated[ImagePreview, Tag("ImagePreview")],
    ],
    Discriminator(get_name),
]


def set_default_component(type: Optional[PortType]) -> Components:
    match type:
        case PortType.INTEGER:
            return NumberField(placeholder="Number field.")
        case PortType.NUMBER:
            return NumberField(placeholder="Number field.")
        case PortType.BOOLEAN:
            return Toggle()
        case PortType.STRING:
            return TextField(placeholder="Text field.")
        case PortType.IMAGE:
            return StorageSelect(supported_ext=[Ext.PNG, Ext.JPG, Ext.JPEG])
        case _:
            return Blank()
