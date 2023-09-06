from transformers import pipeline
from fastapi.exceptions import HTTPException
from pydantic import Field
from hyko_sdk import CoreModel, SDKFunction

func = SDKFunction(
    description="OPUS English to French Translation specialized model",
    requires_gpu=False,
)

class Inputs(CoreModel):
    english_text: str = Field(..., description="English text")

class Params(CoreModel):
    pass

class Outputs(CoreModel):
    french_translated_text: str = Field(..., description="French translated text")


pipe = None

@func.on_startup
async def load():
    global pipe
    if pipe is not None:
        print("Model already loaded")
        return
    pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")


@func.on_execute
async def main(inputs: Inputs , params: Params)-> Outputs:
     
    if pipe is None:
        raise HTTPException(status_code=500, detail="Model is not loaded yet")
    
    translated = pipe(inputs.english_text, max_length=len(inputs.english_text) * 2)[0]["translation_text"] # type: ignore
    return Outputs(french_translated_text=str(translated))



