from enum import Enum
from typing import Annotated, Any, Optional, Union

from pydantic import (
    BaseModel,
    Discriminator,
    Tag,
    ValidationInfo,
    computed_field,
    field_validator,
)

from .components.components import (
    Components,
)
from .components.utils import to_display_name
from .json_schema import Item, PortType, Ref


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

    description: str
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

    callback_id: Optional[str] = None


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

    def add_input(self, new_input: FieldMetadata):
        self.inputs[new_input.name] = new_input

    def add_output(self, new_output: FieldMetadata):
        self.outputs[new_output.name] = new_output

    def add_param(self, new_param: FieldMetadata):
        self.params[new_param.name] = new_param


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


def get_category(v: Any):
    """Category discriminator function."""
    return v.get("category")


MetaData = Annotated[
    Union[
        Annotated[ModelMetaData, Tag(Category.MODEL)],
        Annotated[FunctionMetaData, Tag(Category.FUNCTION)],
        Annotated[UtilsMetaData, Tag(Category.UTILS)],
        Annotated[APIMetaData, Tag(Category.API)],
        Annotated[IOMetaData, Tag(Category.IO)],
    ],
    Discriminator(get_category),
]


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
