import unittest.mock as mock
from typing import Any, Callable, Coroutine, Type

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
    sample_io_data: Type[BaseModel],
    sample_iop_data_json_schema: HykoJsonSchema,
    toolkit_base: ToolkitBase,
):
    input = toolkit_base.set_input(sample_io_data)
    assert isinstance(toolkit_base.inputs, HykoJsonSchema)
    assert input == sample_io_data
    assert toolkit_base.inputs == sample_iop_data_json_schema


def test_toolkit_base_set_output(
    sample_io_data: Type[BaseModel],
    sample_iop_data_json_schema: HykoJsonSchema,
    toolkit_base: ToolkitBase,
):
    output = toolkit_base.set_output(sample_io_data)
    assert isinstance(toolkit_base.outputs, HykoJsonSchema)
    assert output == sample_io_data
    assert toolkit_base.outputs == sample_iop_data_json_schema


def test_toolkit_base_set_param(
    sample_io_data: Type[BaseModel],
    sample_iop_data_json_schema: HykoJsonSchema,
    toolkit_base: ToolkitBase,
):
    output = toolkit_base.set_output(sample_io_data)
    assert isinstance(toolkit_base.outputs, HykoJsonSchema)
    assert output == sample_io_data
    assert toolkit_base.outputs == sample_iop_data_json_schema


def test_get_base_metadata(
    sample_io_data: Type[BaseModel],
    sample_param_data: Type[BaseModel],
    toolkit_base: ToolkitBase,
):
    toolkit_base.set_input(sample_io_data)
    toolkit_base.set_output(sample_io_data)
    toolkit_base.set_param(sample_param_data)

    meta_data = toolkit_base.get_base_metadata()

    assert isinstance(meta_data, MetaDataBase)


def test_dump_metadata(
    sample_io_data: Type[BaseModel],
    sample_param_data: Type[BaseModel],
    toolkit_base: ToolkitBase,
):
    toolkit_base.set_input(sample_io_data)
    toolkit_base.set_output(sample_io_data)
    toolkit_base.set_param(sample_param_data)

    dumped_meta_data = toolkit_base.dump_metadata()

    assert isinstance(dumped_meta_data, str)


@mock.patch("httpx.post")
def test_write(
    mock_post: mock.MagicMock,
    sample_io_data: Type[BaseModel],
    sample_param_data: Type[BaseModel],
    toolkit_base: ToolkitBase,
):
    mock_response = mock.Mock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    toolkit_base.set_input(sample_io_data)
    toolkit_base.set_output(sample_io_data)
    toolkit_base.set_param(sample_param_data)

    with pytest.raises(BaseException):  # noqa: B017
        toolkit_base.write("test", "user", "pass")


#  ToolkitFunction Tests.
def test_on_execute(
    toolkit_function: ToolkitFunction,
    execute: Type[Coroutine[Any, Any, BaseModel]],
    base_model_child: Type[BaseModel],
):
    toolkit_function.on_execute(execute)
    client = TestClient(toolkit_function)

    response = client.post(
        "/execute",
        json={
            "inputs": base_model_child(key="value").model_dump(),
            "params": base_model_child(key="value").model_dump(),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": "success"}


def test_on_execute_with_bad_execute_function(
    toolkit_function: ToolkitFunction,
    bad_execute: Type[Coroutine[Any, Any, BaseModel]],
    base_model_child: Type[BaseModel],
):
    toolkit_function.on_execute(bad_execute)
    client = TestClient(toolkit_function)

    response = client.post(
        "/execute",
        json={
            "inputs": base_model_child(key="value").model_dump(),
            "params": base_model_child(key="value").model_dump(),
        },
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_function_dump_metadata(
    sample_io_data: Type[BaseModel],
    toolkit_function: ToolkitFunction,
    sample_param_data: Type[BaseModel],
):
    toolkit_function.set_input(sample_io_data)
    toolkit_function.set_output(sample_io_data)
    toolkit_function.set_param(sample_param_data)

    toolkit_function.image_name = "test_image"
    toolkit_function.size = 1024
    toolkit_function.absolute_dockerfile_path = "Dockerfile"
    toolkit_function.docker_context = "."

    dumped_meta_data = toolkit_function.dump_metadata()

    assert isinstance(dumped_meta_data, str)


# ToolkitModel Tests.
def test_model_set_startup_params(
    sample_io_data: Type[BaseModel],
    sample_iop_data_json_schema: HykoJsonSchema,
    toolkit_model: ToolkitModel,
):
    startup_params = toolkit_model.set_startup_params(sample_io_data)
    assert isinstance(toolkit_model.startup_params, HykoJsonSchema)
    assert startup_params == sample_io_data
    assert toolkit_model.startup_params == sample_iop_data_json_schema


def test_model_on_startup(
    toolkit_model: ToolkitModel,
    startup: Type[Coroutine[Any, Any, None]],
    base_model_child: Type[BaseModel],
):
    toolkit_model.on_startup(startup)
    client = TestClient(toolkit_model)

    response = client.post(
        "/startup",
        json={
            "startup_params": base_model_child(key="value").model_dump(),
        },
    )

    assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


def test_api_on_call(toolkit_api: ToolkitAPI, sample_call_fn: Callable[[], str]):
    toolkit_api.on_call(sample_call_fn)

    assert toolkit_api.call == sample_call_fn
    assert toolkit_api.call() == "test call"


def test_api_execute(
    toolkit_api: ToolkitAPI,
    base_model_child: Type[BaseModel],
    sample_call_fn_with_params: Callable[[], str],
):
    toolkit_api.set_input(base_model_child)
    toolkit_api.set_param(base_model_child)

    toolkit_api.on_call(sample_call_fn_with_params)

    result = toolkit_api.execute(
        base_model_child(key="key").model_dump(),
        base_model_child(key="output").model_dump(),
    )

    assert result == "test call"
