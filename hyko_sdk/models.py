from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ValidationInfo,
    computed_field,
    field_validator,
)

from .components import (
    Components,
)
from .json_schema import Item, PortType, Ref
from .utils import to_display_name


class Category(str, Enum):
    MODEL = "models"
    FUNCTION = "functions"
    API = "apis"
    UTILS = "utils"
    IO = "IO"


class FieldMetadata(BaseModel):
    type: PortType
    name: str

    @computed_field
    @property
    def display_name(self) -> str:
        return to_display_name(self.name)

    description: Optional[str] = None
    default: Optional[Any] = None
    value: Optional[Any] = None

    items: Optional[Item | Ref] = None

    @field_validator("items")
    @classmethod
    def check_items(cls, v: Optional[Item], info: ValidationInfo) -> Optional[Item]:
        if info.data.get("type") == PortType.ARRAY and v is None:
            raise ValueError("Items must be provided when type is ARRAY")
        return v

    component: Optional[Components] = None

    callback_id: Optional[UUID] = None


class MetaDataBase(BaseModel):
    @computed_field
    @property
    def image(self) -> str:
        return self.category.value + "/" + self.task + "/" + self.name

    name: str
    task: str
    description: str
    category: Category
    icon: Optional[str] = None

    params: dict[str, FieldMetadata] = {}
    inputs: dict[str, FieldMetadata] = {}
    outputs: dict[str, FieldMetadata] = {}

    def add_output(self, output: FieldMetadata):
        self.outputs[output.name] = output

    def add_param(self, param: FieldMetadata):
        self.params[param.name] = param


class FunctionMetaData(MetaDataBase):
    dockerfile_path: str
    docker_context: str


class ModelMetaData(FunctionMetaData):
    startup_params: dict[str, FieldMetadata] = {}


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


class IOMetaData(MetaDataBase):
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
