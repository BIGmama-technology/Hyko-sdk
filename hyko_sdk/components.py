from typing import Annotated, Any, Union

from pydantic import BaseModel, Discriminator, Tag, computed_field


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


class ComplexComponent(Component):
    class SubField(BaseModel):
        type: str
        name: str
        description: str

        component: "Components"

    fields: list[SubField]


class ListComponent(Component):
    component: "Components"


def get_name(v: Any):
    """Name discriminator function."""
    return v.get("name")


Components = Annotated[
    Union[
        Annotated[Toggle, Tag("Toggle")],
        Annotated[Select, Tag("Select")],
        Annotated[Slider, Tag("Slider")],
        Annotated[TextField, Tag("TextField")],
        Annotated[NumberField, Tag("NumberField")],
        Annotated[ComplexComponent, Tag("ComplexComponent")],
        Annotated[Blank, Tag("Blank")],
    ],
    Discriminator(get_name),
]
