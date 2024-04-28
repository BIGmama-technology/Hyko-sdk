from typing import Any, Coroutine, Type

from fastapi import status
from fastapi.testclient import TestClient
from pydantic import BaseModel

from hyko_sdk.definitions import (
    OnCallType,
    ToolkitAPI,
    ToolkitBase,
    ToolkitFunction,
    ToolkitModel,
)
from hyko_sdk.models import (
    CustomJsonSchema,
    MetaDataBase,
    StorageConfig,
)


# ToolkitBase Tests
def test_toolkit_base_set_input(
    sample_io_data: Type[BaseModel],
    sample_iop_data_json_schema: CustomJsonSchema,
    toolkit_base: ToolkitBase,
):
    input = toolkit_base.set_input(sample_io_data)
    assert isinstance(toolkit_base.inputs, CustomJsonSchema)
    assert input == sample_io_data
    assert toolkit_base.inputs == sample_iop_data_json_schema


def test_toolkit_base_set_output(
    sample_io_data: Type[BaseModel],
    sample_iop_data_json_schema: CustomJsonSchema,
    toolkit_base: ToolkitBase,
):
    output = toolkit_base.set_output(sample_io_data)
    assert isinstance(toolkit_base.outputs, CustomJsonSchema)
    assert output == sample_io_data
    assert toolkit_base.outputs == sample_iop_data_json_schema


def test_toolkit_base_set_param(
    sample_io_data: Type[BaseModel],
    sample_iop_data_json_schema: CustomJsonSchema,
    toolkit_base: ToolkitBase,
):
    param = toolkit_base.set_param(sample_io_data)
    assert isinstance(toolkit_base.params, CustomJsonSchema)
    assert param == sample_io_data
    assert toolkit_base.params == sample_iop_data_json_schema


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

    toolkit_function.absolute_dockerfile_path = "Dockerfile"
    toolkit_function.docker_context = "."

    dumped_meta_data = toolkit_function.dump_metadata()

    assert isinstance(dumped_meta_data, str)


# ToolkitModel Tests.
def test_model_set_startup_params(
    sample_io_data: Type[BaseModel],
    sample_iop_data_json_schema: CustomJsonSchema,
    toolkit_model: ToolkitModel,
):
    startup_params = toolkit_model.set_startup_params(sample_io_data)
    assert isinstance(toolkit_model.startup_params, CustomJsonSchema)
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


def test_api_execute(
    toolkit_api: ToolkitAPI,
    base_model_child: Type[BaseModel],
    sample_call_fn_with_params: OnCallType[...],
):
    toolkit_api.set_input(base_model_child)
    toolkit_api.set_param(base_model_child)

    toolkit_api.on_call(sample_call_fn_with_params)

    result = toolkit_api.execute(
        inputs=base_model_child(key="key").model_dump(),
        params=base_model_child(key="output").model_dump(),
        storage_config=StorageConfig(
            refresh_token="test",
            access_token="test",
            host="test",
        ),
    )

    assert result == "test call"
