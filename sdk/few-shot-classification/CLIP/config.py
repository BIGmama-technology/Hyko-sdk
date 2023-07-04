from pydantic import BaseModel, Field
from hyko_sdk.metadata import MetaData, pmodel_to_ports
from hyko_sdk.io import Image, String
from typing import List

# Metadata

name = "clip-vit-large-patch14"
description = "CLIP Model, few shot image classification"
version = "1.0"
category = "Image Classificatoin"
task = "Classifies Image content to one of items in List[classes : list[str]]"


class Inputs(BaseModel):
    img: Image = Field(..., description="Image input by user to be classified")
    classes: List[String] = Field(..., description="List of classes to classify the input image on")


# Parameters to the function like temperature for gpt3. These values are constant  n runtime
class Params(BaseModel):
    pass


class Outputs(BaseModel):
    output_class: String = Field(..., description="The class of the image")
# Function metadata, should always be here

__meta_data__ = MetaData(
    name=name,
    description=description,
    version=version,
    category=category,
    inputs=pmodel_to_ports(Inputs),  # type: ignore
    params=pmodel_to_ports(Params),  # type: ignore
    outputs=pmodel_to_ports(Outputs),  # type: ignore
)

if __name__ == "__main__":
    print(__meta_data__.json(indent=2))
