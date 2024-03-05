from enum import Enum

from pydantic import Field

from hyko_sdk.function import SDKFunction
from hyko_sdk.io import Image
from hyko_sdk.metadata import CoreModel


class SupportedLanguages(str, Enum):
    arabic = "ara"
    english = "eng"
    french = "fra"
    spanish = "spa"


func = SDKFunction(
    description="Extracts text from an image using Tesseract OCR.",
)


@func.set_input
class Inputs(CoreModel):
    image: Image = Field(..., description="Input image.")


@func.set_param
class Params(CoreModel):
    language: SupportedLanguages = Field(..., description="Select your language.")


@func.set_output
class Outputs(CoreModel):
    generated_text: str = Field(..., description="Extracted text.")