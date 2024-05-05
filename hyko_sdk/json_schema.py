from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaMode
from pydantic_core import CoreSchema

from .components import (
    Blank,
    ComplexComponent,
    Components,
    ListComponent,
    NumberField,
    Select,
    SubField,
    TextField,
    Toggle,
)


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


def set_default_component(type: Optional[PortType]) -> Components:
    match type:
        case PortType.INTEGER:
            return NumberField(placeholder="")
        case PortType.NUMBER:
            return NumberField(placeholder="")
        case PortType.BOOLEAN:
            return Toggle()
        case PortType.STRING:
            return TextField(placeholder="")
        case _:
            return Blank()


class Item(BaseModel):
    type: PortType = PortType.ANY
    items: Optional["Item"] = None


class Ref(BaseModel):
    ref: str = Field(..., alias="$ref")

    model_config = ConfigDict(populate_by_name=True)


class Property(BaseModel):
    type: PortType = PortType.ANY
    description: Optional[str] = None
    default: Optional[Any] = None

    items: Optional[Item | Ref] = None

    all_of: Optional[list[Ref]] = Field(default=None, alias="allOf")
    ref: Optional[str] = Field(default=None, alias="$ref")

    show: bool = True
    required: bool = True

    component: Optional[Components] = None

    model_config = ConfigDict(populate_by_name=True)


class EnumDef(BaseModel):
    type: PortType
    enum: list[str | int | float]


class ModelDef(BaseModel):
    properties: dict[str, Property]


class CustomJsonSchema(BaseModel):
    properties: dict[str, Property]
    defs: Optional[dict[str, EnumDef | ModelDef]] = Field(default=None, alias="$defs")

    model_config = ConfigDict(populate_by_name=True)


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

        for _, property in json_schema.properties.items():
            if property.all_of and json_schema.defs:
                _def = json_schema.defs[property.all_of[0].ref]
                if isinstance(_def, EnumDef):
                    property.type = _def.type

            elif property.ref and json_schema.defs:
                property.type = PortType.OBJECT

        return json_schema.model_dump(exclude_none=True)


class JsonSchemaGeneratorWithComponents(JsonSchemaGenerator):
    def generate(self, schema: CoreSchema, mode: JsonSchemaMode = "validation"):
        json_schema = super().generate(schema, mode)
        json_schema = CustomJsonSchema.model_validate(json_schema)

        for _, property in json_schema.properties.items():
            if property.all_of and json_schema.defs:
                _def = json_schema.defs[property.all_of[0].ref]
                if isinstance(_def, EnumDef):
                    property.component = Select(choices=_def.enum)

            elif property.ref and json_schema.defs:
                _def = json_schema.defs[property.ref]
                if isinstance(_def, ModelDef):
                    fields = [
                        SubField(name=name, **prop.model_dump())
                        if prop.component
                        else SubField(
                            name=name,
                            component=set_default_component(prop.type),
                            **prop.model_dump(exclude_none=True),
                        )
                        for name, prop in _def.properties.items()
                    ]
                    property.component = ComplexComponent(fields=fields)

            if property.type == PortType.ARRAY:
                items = property.items
                if isinstance(items, Item):
                    property.component = ListComponent(
                        item_component=set_default_component(items.type)
                    )
                elif isinstance(items, Ref) and json_schema.defs:
                    _def = json_schema.defs[items.ref]
                    assert isinstance(_def, ModelDef)
                    assert property.component
                    property.component = ListComponent(
                        item_component=ComplexComponent(
                            fields=[
                                SubField(name=name, **property.model_dump())
                                for name, property in _def.properties.items()
                            ]
                        )
                    )

            if not property.component:
                property.component = set_default_component(property.type)

        return json_schema.model_dump(exclude_none=True)
