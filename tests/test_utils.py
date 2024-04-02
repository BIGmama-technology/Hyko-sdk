import pytest

from hyko_sdk.utils import to_friendly_types


@pytest.mark.parametrize(
    "model, expected_output",
    [
        ("test_model", {"name": "text", "age": "whole number", "gender": "text"}),
        ("enum_model", {"color": "enum"}),
        ("empty_model", {}),
    ],
)
def test_to_f(
    model: str,
    expected_output: dict[str, str],
    request: pytest.FixtureRequest,
):
    test_model = request.getfixturevalue(model)
    assert to_friendly_types(test_model) == expected_output
