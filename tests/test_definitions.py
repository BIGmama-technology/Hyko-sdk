import unittest.mock as mock

import pytest
from pydantic import BaseModel

from hyko_sdk.definitions import ToolkitBase
from hyko_sdk.models import (
    HykoJsonSchema,
    MetaDataBase,
)


def test_toolkit_base_set_input(
    sample_iop_data: BaseModel, sample_iop_data_json_schema: HykoJsonSchema
):
    toolkit_base = ToolkitBase(
        name="test_function",
        task="task",
        desc="Description",
    )

    input = toolkit_base.set_input(sample_iop_data)  # type: ignore
    assert isinstance(toolkit_base.inputs, HykoJsonSchema)
    assert input == sample_iop_data
    assert toolkit_base.inputs == sample_iop_data_json_schema


def test_toolkit_base_set_output(
    sample_iop_data: BaseModel, sample_iop_data_json_schema: HykoJsonSchema
):
    toolkit_base = ToolkitBase(
        name="test_function",
        task="task",
        desc="Description",
    )

    output = toolkit_base.set_output(sample_iop_data)  # type: ignore
    assert isinstance(toolkit_base.outputs, HykoJsonSchema)
    assert output == sample_iop_data
    assert toolkit_base.outputs == sample_iop_data_json_schema


def test_toolkit_base_set_param(
    sample_iop_data: BaseModel, sample_iop_data_json_schema: HykoJsonSchema
):
    toolkit_base = ToolkitBase(
        name="test_function",
        task="task",
        desc="Description",
    )

    output = toolkit_base.set_output(sample_iop_data)  # type: ignore
    assert isinstance(toolkit_base.outputs, HykoJsonSchema)
    assert output == sample_iop_data
    assert toolkit_base.outputs == sample_iop_data_json_schema


def test_get_base_meta_data(sample_iop_data: BaseModel):
    toolkit_base = ToolkitBase(
        name="test_function",
        task="task",
        desc="Description",
    )

    toolkit_base.set_input(sample_iop_data)  # type: ignore
    toolkit_base.set_output(sample_iop_data)  # type: ignore
    toolkit_base.set_param(sample_iop_data)  # type: ignore

    meta_data = toolkit_base.get_base_metadata()

    assert isinstance(meta_data, MetaDataBase)


def test_dump_metadata(sample_iop_data: BaseModel):
    toolkit_base = ToolkitBase(
        name="test_function",
        task="task",
        desc="Description",
    )

    toolkit_base.set_input(sample_iop_data)  # type: ignore
    toolkit_base.set_output(sample_iop_data)  # type: ignore
    toolkit_base.set_param(sample_iop_data)  # type: ignore

    dumped_meta_data = toolkit_base.dump_metadata()

    assert isinstance(dumped_meta_data, str)


@mock.patch("httpx.post")
def test_write(mock_post: mock.MagicMock, sample_iop_data: BaseModel):
    mock_response = mock.Mock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    toolkit_base = ToolkitBase(
        name="test_function",
        task="task",
        desc="Description",
    )

    toolkit_base.set_input(sample_iop_data)  # type: ignore
    toolkit_base.set_output(sample_iop_data)  # type: ignore
    toolkit_base.set_param(sample_iop_data)  # type: ignore

    with pytest.raises(BaseException):  # noqa: B017
        toolkit_base.write("test", "user", "pass")
