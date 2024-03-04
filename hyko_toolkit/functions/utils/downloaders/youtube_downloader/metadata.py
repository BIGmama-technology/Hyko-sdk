from enum import Enum

from pydantic import Field

from hyko_sdk.function import SDKFunction
from hyko_sdk.io import Video
from hyko_sdk.metadata import CoreModel


class Resolution(str, Enum):
    p720 = "720p"
    p360 = "360p"
    p144 = "144p"
    highest = "highest"
    lowest = "lowest"


func = SDKFunction(description="Download a video from YouTube.")


@func.set_input
class Inputs(CoreModel):
    video_url: str = Field(
        ...,
        description="The URL of the YouTube video to download.",
    )


@func.set_param
class Params(CoreModel):
    resolution: Resolution = Field(
        ...,
        description="The desired resolution of the video.",
    )


@func.set_output
class Outputs(CoreModel):
    output_video: Video = Field(..., description="Output Video.")