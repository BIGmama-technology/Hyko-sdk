from fastapi import HTTPException
from pydantic import Field
from hyko_sdk import CoreModel, SDKFunction
import transformers
import os

func = SDKFunction(
    description="Hugging Face text classification",
    requires_gpu=False,
)


class Inputs(CoreModel):
    input_text: str = Field(..., description="text to classify")


class Params(CoreModel):
    hugging_face_model: str = Field(
        ..., description="Model"
    )  # WARNING: DO NOT REMOVE! implementation specific
    device_map: str = Field(
        ..., description="Device map (Auto, CPU or GPU)"
    )  # WARNING: DO NOT REMOVE! implementation specific


class Outputs(CoreModel):
    label: str = Field(..., description="Class label")
    score: float = Field(..., description="Associated score to the class label")


classifier = None


@func.on_startup
async def load():
    global classifier

    if classifier is not None:
        print("Model already Loaded")
        return

    model = os.getenv("HYKO_HF_MODEL")

    if model is None:
        raise HTTPException(status_code=500, detail="Model env not set")

    device_map = os.getenv("HYKO_DEVICE_MAP", "auto")

    try:
        classifier = transformers.pipeline(
            task="text-classification",
            model=model,
            device_map=device_map,
        )
    except Exception as exc:
        import logging

        logging.error(exc)


@func.on_execute
async def main(inputs: Inputs, params: Params) -> Outputs:
    if classifier is None:
        raise HTTPException(status_code=500, detail="Model is not loaded yet")

    res = classifier(inputs.input_text)

    return Outputs(label=res[0]["label"], score=res[0]["score"])  # type: ignore
