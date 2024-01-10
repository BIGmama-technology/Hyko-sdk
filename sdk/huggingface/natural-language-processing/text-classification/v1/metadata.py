from pydantic import Field

from hyko_sdk.function import SDKFunction
from hyko_sdk.metadata import CoreModel

func = SDKFunction(
    description="Hugging Face text classification",
)


@func.set_input
class Inputs(CoreModel):
    input_text: str = Field(..., description="text to classify")


@func.set_param
class Params(CoreModel):
    hugging_face_model: str = Field(..., description="Model")
    device_map: str = Field(..., description="Device map (Auto, CPU or GPU)")


@func.set_output
class Outputs(CoreModel):
    label: str = Field(..., description="Class label")
    score: float = Field(..., description="Associated score to the class label")