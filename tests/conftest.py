from enum import Enum
from typing import Type

import numpy as np
import PIL.Image as PIL_Image
import pytest
from pydantic import BaseModel, Field

from hyko_sdk.io import Image
from hyko_sdk.models import CoreModel, HykoJsonSchema
from hyko_sdk.utils import to_friendly_types


@pytest.fixture
def sample_iop_data_json_schema(sample_iop_data: Type[BaseModel]):
    return HykoJsonSchema(
        **sample_iop_data.model_json_schema(),
        friendly_types=to_friendly_types(sample_iop_data),
    )


@pytest.fixture
def sample_iop_data():
    class IOP(CoreModel):
        input_image: Image = Field(..., description="IOP image")

    return IOP


# io_tests fixtures
@pytest.fixture
def sample_nd_array_data():
    return np.zeros((100, 100, 3), dtype=np.uint8)


@pytest.fixture
def sample_audio_data():
    rate = 16000
    return np.random.uniform(-1, 1, rate)


@pytest.fixture
def sample_pil_image_data() -> PIL_Image.Image:
    width, height = 100, 100
    nd_image = np.zeros((height, width, 3), dtype=np.uint8)
    pil_image = PIL_Image.fromarray(nd_image)
    return pil_image


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
