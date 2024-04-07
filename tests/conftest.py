from enum import Enum
from typing import Any, Dict, Type

import numpy as np
import PIL.Image as PIL_Image
import pytest
from pydantic import BaseModel, Field

from hyko_sdk.definitions import ToolkitAPI, ToolkitBase, ToolkitFunction, ToolkitModel
from hyko_sdk.io import Audio, Image, Video
from hyko_sdk.models import CoreModel, HykoJsonSchema, StorageConfig
from hyko_sdk.utils import to_friendly_types


@pytest.fixture(autouse=True)
def setup_storage_config():
    StorageConfig.configure("test", "test", "test")


@pytest.fixture
def sample_call_fn_with_params():
    def test_call(inputs: Dict[str, Any], params: Dict[str, Any]):
        return "test call"

    return test_call


@pytest.fixture
def base_model_child():
    class BaseModelChild(BaseModel):
        key: str

    return BaseModelChild


@pytest.fixture
def execute():
    async def execute_fn(inputs: BaseModel, params: BaseModel) -> BaseModel:
        class Output(BaseModel):
            result: str

        return Output(result="success")

    return execute_fn


@pytest.fixture
def bad_execute():
    async def bad_execute(inputs: BaseModel, params: BaseModel) -> BaseModel:
        raise Exception("Bad execute")

    return bad_execute


@pytest.fixture
def startup():
    async def startup(start_params: BaseModel):
        pass

    return startup


@pytest.fixture
def toolkit_base():
    return ToolkitBase(name="Test Toolkit", task="Testing", desc="A test toolkit base")


@pytest.fixture
def toolkit_function():
    return ToolkitFunction(
        name="test_function", task="task", description="A test function"
    )


@pytest.fixture
def toolkit_model():
    return ToolkitModel(
        name="test_function",
        task="task",
        description="Description",
    )


@pytest.fixture
def toolkit_api():
    return ToolkitAPI(name="test", task="task", description="Description")


@pytest.fixture
def sample_iop_data_json_schema(sample_io_data: Type[BaseModel]):
    return HykoJsonSchema(
        **sample_io_data.model_json_schema(),
        friendly_types=to_friendly_types(sample_io_data),
    )


@pytest.fixture
def sample_io_data():
    class IO(CoreModel):
        sample_io_image: Image = Field(..., description="IO image")
        sample_io_audio: Audio = Field(..., description="IO audio")
        sample_io_video: Video = Field(..., description="IO video")

    return IO


@pytest.fixture
def sample_param_data():
    class Param(CoreModel):
        min: int
        max: int

    return Param


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
