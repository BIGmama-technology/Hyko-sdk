import openai
from pydantic import Field
from hyko_sdk import CoreModel, SDKFunction
from typing import Optional


func = SDKFunction(
    description="OpenAI's GPT 3.5 Turbo Large completion model (API)",
    requires_gpu=False,
)


class Inputs(CoreModel):
    prompt: str = Field(..., description="Input prompt (16k tokens max context size)")

class Params(CoreModel):
    system_prompt: Optional[str] = Field(default=None, description='System prompt for the model (used to instruct the model)')
    api_key: str = Field(..., description="OpenAI's API KEY")
    max_tokens: Optional[int] = Field(default=None, description="Maximum number of tokens generated by the model")
    temperature: Optional[float] = Field(default=None, description="Model's temperature")
    top_p: Optional[float] = Field(default=None, description="Model's Top P")

class Outputs(CoreModel):
    completion_text: str = Field(..., description="Completion text")


@func.on_execute
async def main(inputs: Inputs, params: Params):

    if params.system_prompt is None:
        messages=[
            {
                "role": "user",
                "content": inputs.prompt
            },
        ]
    else:
        messages=[
            {
                "role": "system",
                "content": params.system_prompt,
            },
            {
                "role": "user",
                "content": inputs.prompt
            },
        ]

    chat_completion = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo-16k",
        messages=messages,
        api_key=params.api_key,
        max_tokens=params.max_tokens,
        temperature=params.temperature,
        top_p=params.top_p,
    )

    completion: str = chat_completion.choices[0].message.content # type: ignore

    return Outputs(completion_text=completion)

