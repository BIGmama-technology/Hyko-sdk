from enum import Enum
from typing import Annotated, Any, Optional, Union

from pydantic import BaseModel, Discriminator, Tag, computed_field

from hyko_sdk.components.utils import to_display_name


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
    CSV = "csv"

    ANY = "any"
    OBJECT = "object"


class Component(BaseModel):
    freezed: bool = False

    @computed_field
    @property
    def name(self) -> str:
        return self.__class__.__name__


class Slider(Component):
    leq: int
    geq: int
    step: float = 1


class Toggle(Component):
    pass


class SelectChoice(BaseModel):
    label: str | int | float
    value: str | int | float


class Select(Component):
    choices: list[SelectChoice]


class Search(Component):
    placeholder: str
    results: list[str] = []


class TextField(Component):
    placeholder: str
    multiline: bool = False
    secret: bool = False


class NumberField(Component):
    placeholder: str

    leq: Optional[int] = None
    geq: Optional[int] = None
    step: Optional[float] = None


class SubField(BaseModel):
    type: str
    name: str
    description: str

    @computed_field
    @property
    def display_name(self) -> str:
        return to_display_name(self.name)

    component: Optional["Components"] = None


class StorageSelect(Component):
    supported_ext: list[Ext]


class ImagePreview(Component):
    pass


class VideoPreview(Component):
    pass


class TextPreview(Component):
    pass


class PDFPreview(Component):
    pass


class AudioPreview(Component):
    pass


class ComplexComponent(Component):
    fields: list[SubField]


class ListComponent(Component):
    item_component: Optional["Components"] = None


class ButtonComponent(Component):
    text: str


class RefreshableSelect(Select):
    callback_id: str


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
        Annotated[Search, Tag("Search")],
        Annotated[Slider, Tag("Slider")],
        Annotated[TextField, Tag("TextField")],
        Annotated[NumberField, Tag("NumberField")],
        Annotated[ComplexComponent, Tag("ComplexComponent")],
        Annotated[ListComponent, Tag("ListComponent")],
        Annotated[StorageSelect, Tag("StorageSelect")],
        Annotated[ImagePreview, Tag("ImagePreview")],
        Annotated[VideoPreview, Tag("VideoPreview")],
        Annotated[TextPreview, Tag("TextPreview")],
        Annotated[PDFPreview, Tag("PDFPreview")],
        Annotated[AudioPreview, Tag("AudioPreview")],
        Annotated[ButtonComponent, Tag("ButtonComponent")],
        Annotated[RefreshableSelect, Tag("RefreshableSelect")],
    ],
    Discriminator(get_name),
]


def set_default_component(type: Optional[PortType]) -> Components | None:
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
        case PortType.VIDEO:
            return StorageSelect(
                supported_ext=[
                    Ext.MPEG,
                    Ext.WEBM,
                    Ext.MP4,
                    Ext.AVI,
                    Ext.MKV,
                    Ext.MOV,
                    Ext.WMV,
                ]
            )
        case PortType.AUDIO:
            return StorageSelect(supported_ext=[Ext.WAV, Ext.MP3])
        case PortType.PDF:
            return StorageSelect(supported_ext=[Ext.PDF])
        case _:
            return None
