from typing import Type

from pydantic import BaseModel

from hyko_sdk.utils import to_friendly_types


def test_to_friendly_types_with_valid_input(test_model: Type[BaseModel]):
    expected_output = {"name": "text", "age": "whole number", "gender": "text"}
    assert to_friendly_types(test_model) == expected_output


def test_to_friendly_types_with_enum(enum_model: Type[BaseModel]):
    expected_output = {"color": "enum"}
    assert to_friendly_types(enum_model) == expected_output


def test_to_friendly_types_with_empty_model(empty_model: Type[BaseModel]):
    assert to_friendly_types(empty_model) == {}
