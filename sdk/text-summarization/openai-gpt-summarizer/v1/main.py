from enum import Enum
from typing import Optional

import openai
from pydantic import Field

from hyko_sdk.function import SDKFunction
from hyko_sdk.metadata import CoreModel

func = SDKFunction(
    description="OpenAI GPT Summarization models (API)",
    requires_gpu=False,
)


class SelectedModel(str, Enum):
    GPT_3_5 = "gpt-3.5-turbo"
    GPT_3_5_16K = "gpt-3.5-turbo-16k"
    GPT_4 = "gpt-4"
    GPT_4_32K = "gpt-4-32k"


class Inputs(CoreModel):
    text: str = Field(..., description="Input text")


class Params(CoreModel):
    model: SelectedModel = Field(
        ..., description="Model variant to be used for summarization"
    )
    api_key: str = Field(..., description="OpenAI API KEY")
    max_tokens: Optional[int] = Field(
        default=None, description="Maximum number of tokens generated by the model"
    )
    temperature: Optional[float] = Field(default=None, description="Model temperature")
    top_p: Optional[float] = Field(default=None, description="Model Top P")


class Outputs(CoreModel):
    summary: str = Field(..., description="Summarized text")


@func.on_execute
async def main(inputs: Inputs, params: Params) -> Outputs:
    chat_completion = await openai.ChatCompletion.acreate(
        model=params.model,
        messages=[
            {
                "role": "system",
                "content": "Summarize this",
            },
            {
                "role": "user",
                "content": inputs.text,
            },
        ],
        api_key=params.api_key,
        max_tokens=params.max_tokens,
        temperature=params.temperature,
        top_p=params.top_p,
    )

    completion: str = chat_completion.choices[0].message.content  # type: ignore

    return Outputs(summary=completion)
