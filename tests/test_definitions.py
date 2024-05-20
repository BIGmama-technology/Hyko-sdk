from typing import Type

from pydantic import BaseModel

from hyko_sdk.definitions import (
    OnCallType,
    ToolkitAPI,
    ToolkitBase,
    ToolkitFunction,
    ToolkitModel,
)
from hyko_sdk.models import (
    HykoJsonSchema,
    MetaDataBase,
    StorageConfig,
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
    param = toolkit_base.set_param(sample_io_data)
    assert isinstance(toolkit_base.params, HykoJsonSchema)
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


def toolkit_test(
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
    result = toolkit.call(
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


def test_api_execute(
    toolkit_api: ToolkitAPI,
    base_model_child: Type[BaseModel],
    sample_call_fn_with_params: OnCallType[...],
):
    toolkit_test(toolkit_api, base_model_child, sample_call_fn_with_params)


def test_functions_execute(
    toolkit_function: ToolkitFunction,
    base_model_child: Type[BaseModel],
    sample_call_fn_with_params: OnCallType[...],
):
    toolkit_test(toolkit_function, base_model_child, sample_call_fn_with_params)


def test_model_execute(
    toolkit_model: ToolkitModel,
    base_model_child: Type[BaseModel],
    sample_call_fn_with_params: OnCallType[...],
):
    toolkit_test(toolkit_model, base_model_child, sample_call_fn_with_params)
