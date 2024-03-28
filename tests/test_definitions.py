from pydantic import BaseModel

from hyko_sdk.definitions import ToolkitFunction
from hyko_sdk.models import (
    HykoJsonSchema,
)


def test_toolkit_base_set_input(
    sample_iop_data: BaseModel, sample_iop_data_json_schema: HykoJsonSchema
):
    toolkit_function = ToolkitFunction(
        name="test_function",
        task="task",
        description="Description",
    )

    input = toolkit_function.set_input(sample_iop_data)  # type: ignore
    assert isinstance(toolkit_function.inputs, HykoJsonSchema)
    assert input == sample_iop_data
    assert toolkit_function.inputs == sample_iop_data_json_schema


def test_toolkit_base_set_output(
    sample_iop_data: BaseModel, sample_iop_data_json_schema: HykoJsonSchema
):
    toolkit_function = ToolkitFunction(
        name="test_function",
        task="task",
        description="Description",
    )

    output = toolkit_function.set_output(sample_iop_data)  # type: ignore
    assert isinstance(toolkit_function.outputs, HykoJsonSchema)
    assert output == sample_iop_data
    assert toolkit_function.outputs == sample_iop_data_json_schema


def test_toolkit_base_set_param(
    sample_iop_data: BaseModel, sample_iop_data_json_schema: HykoJsonSchema
):
    toolkit_function = ToolkitFunction(
        name="test_function",
        task="task",
        description="Description",
    )

    output = toolkit_function.set_output(sample_iop_data)  # type: ignore
    assert isinstance(toolkit_function.outputs, HykoJsonSchema)
    assert output == sample_iop_data
    assert toolkit_function.outputs == sample_iop_data_json_schema
