from enum import Enum
from typing import Annotated, Any, Literal, Optional

from pydantic import (
    BaseModel,
    ValidationInfo,
    computed_field,
    field_validator,
)

from hyko_sdk.utils import to_image

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
    IO = "io"


class SupportedProviders(str, Enum):
    """Supported third-party providers."""

    GITHUB = "github"
    DISCORD = "discord"
    NOTION = "notion"
    AIRTABLE = "airtable"
    TWITTER = "twitter"
    REDDIT = "reddit"
    OUTLOOK = "outlook"
    DRIVE = "drive"
    DOCS = "docs"
    SHEETS = "sheets"
    GMAIL = "gmail"
    YOUTUBE = "youtube"


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
    refresh_id: Optional[str] = None


Icon = Literal[
    "openai",
    "io",
    "functions",
    "models",
    "apis",
    "utils",
    "hf",
    "openrouter",
    "docs",
    "sheets",
    "discord",
    "airtable",
    "youtube",
    "google",
    "gmail",
    "github",
    "drive",
    "notion",
    "outlook",
    "x",
    "reddit",
    "cohere",
    "anthropic",
    "arxiv",
    "duckduckgo",
    "gemini",
    "microsoft",
    "mistral",
    "stabilityai",
    "groq",
    "replicate",
    "wikipedia",
    "tune",
    "text",
    "number",
    "image",
    "audio",
    "video",
    "csv",
    "list",
    "pdf",
    "graph",
    "flip",
    "dimensions",
    "crop",
    "opacity",
    "padding",
    "resize",
    "rotate",
    "stack",
]


class MetaDataBase(BaseModel):
    @computed_field
    @property
    def image(self) -> str:
        return to_image(self.category.value + "/" + self.task + "/" + self.name)

    name: str
    task: str
    description: str
    category: Category
    cost: int = 0
    auth: Optional[SupportedProviders] = None

    icon: Optional[Annotated[str, Icon]] = None

    params: dict[str, FieldMetadata] = {}
    inputs: dict[str, FieldMetadata] = {}
    outputs: dict[str, FieldMetadata] = {}

    def add_input(self, new_input: FieldMetadata):
        self.inputs[new_input.name] = new_input

    def add_output(self, new_output: FieldMetadata):
        self.outputs[new_output.name] = new_output

    def add_param(self, new_param: FieldMetadata):
        self.params[new_param.name] = new_param


class Method(str, Enum):
    get = "GET"
    post = "POST"
    patch = "PATCH"
    put = "PUT"
    delete = "DELETE"


def get_category(v: Any):
    """Category discriminator function."""
    return v.get("category")


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
