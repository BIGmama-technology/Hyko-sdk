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
from .json_schema import Item, PortType, Ref
from .utils import to_display_name


class Category(str, Enum):
    MODEL = "models"
    FUNCTION = "functions"
    API = "apis"
    UTILS = "utils"
    IO = "IO"


class FieldMetadata(BaseModel):
    type: str
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
