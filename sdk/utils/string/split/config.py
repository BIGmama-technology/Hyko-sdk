from pydantic import BaseModel
from hyko_sdk.io import String
from hyko_sdk.metadata import MetaData, pmodel_to_ports

# Change Meta data here:#####################

name = "Split"
description = "Split a string to a list of strings based on delimiter"
version = "1.0"
category = "utils/string"

##############################################


# Change types of inputs and outputs here:#####################

# main inputs to the function like a prompt for gpt3. These values are dynamic in runtime.
class Inputs(BaseModel):
    text: String


# runtime means when the prototype is generated and deployed for the user (ui and all)


# Parameters to the function like temperature for gpt3. These values are constant  n runtime
class Params(BaseModel):
    delimeter: String


# outputs of the function.
class Outputs(BaseModel):
    splitted: list[String]


# Function metadata, should always be here

__meta_data__ = MetaData(
    name=name,
    description=description,
    version=version,
    category=category,
    inputs=pmodel_to_ports(Inputs), # type: ignore
    params=pmodel_to_ports(Params), # type: ignore
    outputs=pmodel_to_ports(Outputs), # type: ignore
)


if __name__ == "__main__":
    print(__meta_data__.json(indent=2))