from typing import Union

from pydantic import BaseModel, computed_field


class Component(BaseModel):
    place_holder: str

    @computed_field
    @property
    def name(self) -> str:
        return self.__class__.__name__


class Slider(Component):
    leq: int
    geq: int


class Divider(Component):
    pass


Components = Union[
    Slider,
    Divider,
]
