import io
from enum import Enum
from typing import Any, Dict
from unittest import mock

import numpy as np
import PIL
import PIL.Image
import pytest
from PIL.Image import Image as PILImage
from pydantic import BaseModel, Field

from hyko_sdk.definitions import ToolkitAPI, ToolkitBase, ToolkitFunction, ToolkitModel
from hyko_sdk.io import Audio, Image, Video, field
from hyko_sdk.models import CoreModel, StorageConfig


@pytest.fixture(autouse=True)
def configure_settings():
    StorageConfig.configure("test", "test", "test")


@pytest.fixture
def mock_post_success():
    with mock.patch("httpx.AsyncClient.post") as mock_post:
        # Setup a mock response object
        mock_response = mock.Mock()
        mock_response.is_success = True
        mock_response.json = lambda: "test_filename"
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_get_audio(sample_audio_data: np.ndarray[Any, Any]):
    with mock.patch("httpx.AsyncClient.get") as mock_get:
        # Setup a mock response object
        mock_response = mock.Mock()
        mock_response.is_success = True
        mock_response.content = sample_audio_data.tobytes()
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_get_png(sample_pil_image_data: PILImage):
    with mock.patch("httpx.AsyncClient.get") as mock_post:
        # Setup a mock response object
        file = io.BytesIO()
        sample_pil_image_data.save(file, format="PNG")
        img_byte = file.getvalue()

        mock_response = mock.Mock()
        mock_response.is_success = True
        mock_response.content = img_byte
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def sample_call_fn_with_params():
    def test_call(inputs: Dict[str, Any], params: Dict[str, Any]):
        return "test call"

    return test_call


@pytest.fixture
def base_model_child():
    class BaseModelChild(BaseModel):
        key: str = Field(..., description="test")

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
        name="test_function",
        task="task",
        description="A test function",
        docker_context="test_context",
        absolute_dockerfile_path="test_dockerfile_path",
    )


@pytest.fixture
def toolkit_model():
    return ToolkitModel(
        name="test_function",
        task="task",
        description="Description",
        docker_context="test_context",
        absolute_dockerfile_path="test_dockerfile_path",
    )


@pytest.fixture
def toolkit_api():
    return ToolkitAPI(name="test", task="task", description="Description")


@pytest.fixture
def sample_io_data():
    class IO(CoreModel):
        sample_io_image: Image = field(description="test IO image")
        sample_io_audio: Audio = field(description="test IO audio")
        sample_io_video: Video = field(description="test IO video")

    return IO


@pytest.fixture
def sample_param_data():
    class Param(CoreModel):
        min: int = Field(..., description="test")
        max: int = Field(..., description="test")

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
def sample_pil_image_data() -> PILImage:
    width, height = 100, 100
    nd_image = np.zeros((height, width, 3), dtype=np.uint8)
    pil_image = PIL.Image.fromarray(nd_image)
    return pil_image


# test_utils fixtures.
@pytest.fixture
def test_model():
    class TestModel(BaseModel):
        name: str = Field(..., description="test")
        age: int = Field(..., description="test")
        gender: str = Field(..., description="test")

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
