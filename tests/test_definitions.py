from typing import Type

import pytest
from pydantic import BaseModel

from hyko_sdk.definitions import (
    OnCallType,
    ToolkitBase,
    ToolkitFunction,
)
from hyko_sdk.models import (
    FieldMetadata,
    MetaDataBase,
    StorageConfig,
)


# ToolkitBase Tests
def test_toolkit_base_set_input(
    sample_io_data: Type[BaseModel],
    toolkit_base: ToolkitBase,
):
    input = toolkit_base.set_input(sample_io_data)
    assert toolkit_base.inputs
    assert all(
        isinstance(field, FieldMetadata) for field in toolkit_base.inputs.values()
    )
    assert input == sample_io_data


def test_toolkit_base_set_output(
    sample_io_data: Type[BaseModel],
    toolkit_base: ToolkitBase,
):
    output = toolkit_base.set_output(sample_io_data)
    assert toolkit_base.outputs
    assert all(
        isinstance(field, FieldMetadata) for field in toolkit_base.outputs.values()
    )
    assert output == sample_io_data


def test_toolkit_base_set_param(
    sample_io_data: Type[BaseModel],
    toolkit_base: ToolkitBase,
):
    param = toolkit_base.set_param(sample_io_data)
    assert toolkit_base.params
    assert all(
        isinstance(field, FieldMetadata) for field in toolkit_base.params.values()
    )
    assert param == sample_io_data


def test_get_metadata(
    sample_io_data: Type[BaseModel],
    sample_param_data: Type[BaseModel],
    toolkit_base: ToolkitBase,
):
    toolkit_base.set_input(sample_io_data)
    toolkit_base.set_output(sample_io_data)
    toolkit_base.set_param(sample_param_data)

    meta_data = toolkit_base.get_metadata()

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


def test_function_dump_metadata(
    sample_io_data: Type[BaseModel],
    toolkit_function: ToolkitFunction,
    sample_param_data: Type[BaseModel],
):
    toolkit_function.set_input(sample_io_data)
    toolkit_function.set_output(sample_io_data)
    toolkit_function.set_param(sample_param_data)

    dumped_meta_data = toolkit_function.dump_metadata()

    assert isinstance(dumped_meta_data, str)


@pytest.mark.asyncio
async def toolkit_test(
    toolkit: ToolkitBase,
    base_model_child: Type[BaseModel],
    sample_call_fn_with_params: OnCallType[...],
):
    # Set the input and parameter models for the toolkit
    toolkit.set_input(base_model_child)
    toolkit.set_param(base_model_child)

    # Set the sample call function with parameters
    toolkit.on_call(sample_call_fn_with_params)

    # Call the execute function with test inputs, params, and storage config
    result = await toolkit.call(
        inputs=base_model_child(key="key").model_dump(),
        params=base_model_child(key="output").model_dump(),
        storage_config=StorageConfig(
            refresh_token="test",
            access_token="test",
            host="test",
        ),
    )

    # Assert the expected result
    assert result == "test call"
