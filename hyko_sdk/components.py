from typing import Union

from pydantic import BaseModel, computed_field


class Component(BaseModel):
    @computed_field
    @property
    def name(self) -> str:
        return self.__class__.__name__


class Slider(Component):
    leq: int
    geq: int


class Select(Component):
    choices: list[str | int | float]


Components = Union[Slider, Select]
