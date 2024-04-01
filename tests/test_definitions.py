import unittest.mock as mock
from typing import Any, Dict, Type

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import BaseModel

from hyko_sdk.definitions import ToolkitAPI, ToolkitBase, ToolkitFunction, ToolkitModel
from hyko_sdk.models import (
    HykoJsonSchema,
    MetaDataBase,
)


# ToolkitBase Tests
def test_toolkit_base_set_input(
    sample_io_data: Type[BaseModel], sample_iop_data_json_schema: HykoJsonSchema
):
    toolkit_base = ToolkitBase(
        name="test_function",
        task="task",
        desc="Description",
    )

    input = toolkit_base.set_input(sample_io_data)
    assert isinstance(toolkit_base.inputs, HykoJsonSchema)
    assert input == sample_io_data
    assert toolkit_base.inputs == sample_iop_data_json_schema


def test_toolkit_base_set_output(
    sample_io_data: Type[BaseModel], sample_iop_data_json_schema: HykoJsonSchema
):
    toolkit_base = ToolkitBase(
        name="test_function",
        task="task",
        desc="Description",
    )

    output = toolkit_base.set_output(sample_io_data)
    assert isinstance(toolkit_base.outputs, HykoJsonSchema)
    assert output == sample_io_data
    assert toolkit_base.outputs == sample_iop_data_json_schema


def test_toolkit_base_set_param(
    sample_io_data: Type[BaseModel], sample_iop_data_json_schema: HykoJsonSchema
):
    toolkit_base = ToolkitBase(
        name="test_function",
        task="task",
        desc="Description",
    )

    output = toolkit_base.set_output(sample_io_data)
    assert isinstance(toolkit_base.outputs, HykoJsonSchema)
    assert output == sample_io_data
    assert toolkit_base.outputs == sample_iop_data_json_schema


def test_get_base_metadata(sample_io_data: Type[BaseModel]):
    toolkit_base = ToolkitBase(
        name="test_function",
        task="task",
        desc="Description",
    )

    toolkit_base.set_input(sample_io_data)
    toolkit_base.set_output(sample_io_data)
    toolkit_base.set_param(sample_io_data)

    meta_data = toolkit_base.get_base_metadata()

    assert isinstance(meta_data, MetaDataBase)


def test_dump_metadata(sample_io_data: Type[BaseModel]):
    toolkit_base = ToolkitBase(
        name="test_function",
        task="task",
        desc="Description",
    )

    toolkit_base.set_input(sample_io_data)
    toolkit_base.set_output(sample_io_data)
    toolkit_base.set_param(sample_io_data)

    dumped_meta_data = toolkit_base.dump_metadata()

    assert isinstance(dumped_meta_data, str)


@mock.patch("httpx.post")
def test_write(mock_post: mock.MagicMock, sample_io_data: Type[BaseModel]):
    mock_response = mock.Mock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    toolkit_base = ToolkitBase(
        name="test_function",
        task="task",
        desc="Description",
    )

    toolkit_base.set_input(sample_io_data)
    toolkit_base.set_output(sample_io_data)
    toolkit_base.set_param(sample_io_data)

    with pytest.raises(BaseException):  # noqa: B017
        toolkit_base.write("test", "user", "pass")


#  ToolkitFunction Tests.
def test_on_execute():
    toolkit_function = ToolkitFunction(
        name="TestFunction", task="TestTask", description="Test Description"
    )

    class Inputs(BaseModel):
        key: str

    class Params(BaseModel):
        key: str

    async def execute(inputs: BaseModel, params: BaseModel) -> BaseModel:
        class Output(BaseModel):
            result: str

        return Output(result="success")

    toolkit_function.on_execute(execute)

    client = TestClient(toolkit_function)

    response = client.post(
        "/execute",
        json={
            "inputs": Inputs(key="value").model_dump(),
            "params": Params(key="value").model_dump(),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}


def test_on_execute_with_bad_execute_function():
    toolkit_function = ToolkitFunction(
        name="TestFunction", task="TestTask", description="Test Description"
    )

    class Inputs(BaseModel):
        key: str

    class Params(BaseModel):
        key: str

    async def bad_execute(inputs: BaseModel, params: BaseModel) -> BaseModel:
        raise Exception("Bad execute")

    toolkit_function.on_execute(bad_execute)
    client = TestClient(toolkit_function)

    response = client.post(
        "/execute",
        json={
            "inputs": Inputs(key="value").model_dump(),
            "params": Params(key="value").model_dump(),
        },
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_build_with_invalid_dockerfile_path():
    toolkit_function = ToolkitFunction(
        name="test_function",
        task="task",
        description="Description",
    )

    with pytest.raises(BaseException):  # noqa: B017
        toolkit_function.build(dockerfile_path="invalid/path")


def test_build():
    toolkit_function = ToolkitFunction(
        name="test_function", task="task", description="Description"
    )

    toolkit_function.image_name = "test_image_name"
    dockerfile_path = "Dockerfile"
    toolkit_function.build(dockerfile_path=dockerfile_path)

    assert isinstance(toolkit_function.size, int)


def test_function_dump_metadata(sample_io_data: Type[BaseModel]):
    toolkit_function = ToolkitFunction(
        name="test_function",
        task="task",
        description="Description",
    )

    toolkit_function.set_input(sample_io_data)
    toolkit_function.set_output(sample_io_data)
    toolkit_function.set_param(sample_io_data)

    toolkit_function.image_name = "test_image"
    toolkit_function.size = 1024

    dumped_meta_data = toolkit_function.dump_metadata()

    assert isinstance(dumped_meta_data, str)


# ToolkitModel Tests.
def test_model_set_startup_params(
    sample_io_data: Type[BaseModel], sample_iop_data_json_schema: HykoJsonSchema
):
    toolkit_model = ToolkitModel(
        name="test_function",
        task="task",
        description="Description",
    )

    startup_params = toolkit_model.set_startup_params(sample_io_data)
    assert isinstance(toolkit_model.startup_params, HykoJsonSchema)
    assert startup_params == sample_io_data
    assert toolkit_model.startup_params == sample_iop_data_json_schema


def test_model_on_startup():
    toolkit_model = ToolkitModel(name="test", task="task", description="Description")

    class Params(BaseModel):
        key: str

    async def startup(start_params: BaseModel):
        pass

    toolkit_model.on_startup(startup)

    client = TestClient(toolkit_model)

    response = client.post(
        "/startup",
        json={
            "startup_params": Params(key="value").model_dump(),
        },
    )

    assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


def test_api_on_call():
    toolkit_api = ToolkitAPI(name="test", task="task", description="Description")

    def test_call():
        return "test call"

    toolkit_api.on_call(test_call)

    assert toolkit_api.call == test_call
    assert toolkit_api.call() == "test call"


def test_api_execute(sample_io_data: BaseModel):
    toolkit_api = ToolkitAPI(name="test", task="task", description="Description")

    def test_call(inputs: Dict[str, Any], outputs: Dict[str, Any]):
        return "test call"

    class Params(BaseModel):
        key: str

    toolkit_api.set_input(Params)
    toolkit_api.set_param(Params)

    toolkit_api.on_call(test_call)

    result = toolkit_api.execute(
        Params(key="key").model_dump(), Params(key="output").model_dump()
    )

    assert result == "test call"
