from enum import Enum
from typing import Any, Dict, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    computed_field,
    field_validator,
)
from pydantic.json_schema import (
    GenerateJsonSchema,
    JsonSchemaMode,
)
from pydantic_core import CoreSchema

from hyko_sdk.components import Components, Select
from hyko_sdk.utils import to_display_name


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


class Item(BaseModel):
    type: PortType
    items: Optional["Item"] = None


class Ref(BaseModel):
    ref: str = Field(..., alias="$ref")

    model_config = ConfigDict(populate_by_name=True)


class Property(BaseModel):
    type: PortType = PortType.ANY
    description: str
    default: Optional[Any] = None

    items: Optional[Item] = None

    all_of: Optional[list[Ref]] = Field(default=None, alias="allOf")

    show: bool = True
    required: bool = True
    component: Optional[Components] = None

    model_config = ConfigDict(populate_by_name=True)


class EnumProperty(BaseModel):
    type: PortType
    enum: list[str | int | float]


class CustomJsonSchema(BaseModel):
    properties: Dict[str, Property]
    defs: Optional[Dict[str, EnumProperty]] = Field(default=None, alias="$defs")


class JsonSchemaGenerator(GenerateJsonSchema):
    def __init__(
        self,
        by_alias: bool,
        ref_template: str,
    ):
        super().__init__(by_alias, ref_template)

    def generate(self, schema: CoreSchema, mode: JsonSchemaMode = "validation"):
        json_schema = super().generate(schema, mode=mode)
        json_schema = CustomJsonSchema.model_validate(json_schema)

        for field, property in json_schema.properties.items():
            if property.all_of and json_schema.defs:
                enum_property = json_schema.defs[property.all_of[0].ref]

                json_schema.properties[field].type = enum_property.type
                json_schema.properties[field].component = Select(
                    choices=enum_property.enum
                )

        return json_schema.model_dump()


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

    component: Optional[Components] = None


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
