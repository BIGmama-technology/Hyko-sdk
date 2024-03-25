from enum import Enum

import pytest
from pydantic import BaseModel


# test_utils fixtures.
@pytest.fixture
def test_model():
    class TestModel(BaseModel):
        name: str
        age: int
        gender: str

    return TestModel


@pytest.fixture
def enum_model():
    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    class EnumModel(BaseModel):
        color: Color

    return EnumModel


@pytest.fixture
def empty_model():
    class EmptyModel(BaseModel):
        pass

    return EmptyModel
