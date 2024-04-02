<!-- x-release-please-start-version -->
 ![Static Badge](https://img.shields.io/badge/Release-v4.0.2-/?style=flat&logo=track)
<!-- x-release-please-end -->

# Hyko python SDK
## Table of contents

## Description 
[Hyko python sdk](https://github.com/BIGmama-technology/Hyko-sdk) is a python package that allows you to define functions/models and APIs used inside [Hyko toolkit](https://github.com/BIGmama-technology/Hyko-toolkit).

under `hyko_sdk/definitions.py` we find the classes `ToolkitFunction` `ToolkitModel` and `ToolkitAPI` which inherit from the class `ToolkitBase`.

the job of these classes is to define the `deploy` function which is the routine on how to check the coherency of the function and write its metadata to hyko db. 

these classes also define the following decorators :

`@set_input` `@set_output` and `@set_param`  which decorates a pydantic model of the inputs, params and outputs of the node respectively

- ToolkitFunction as well defines :
`@on_execute` which decorates the execution function

- ToolkitModel inherit from ToolkitFunction as well defines :
`@on_startup` which decorates the startup function of the model (e.g. loading the weights)

`@set_startup_params` which decorates the startup params pydantic model
 
`@on_shutdown` which decorate the shutdown function

> example of usage can be found in [Hyko toolkit](https://github.com/BIGmama-technology/Hyko-toolkit)

## Dev requirements
- [Poetry](https://python-poetry.org/docs/#installation)
- [Pyenv](https://github.com/pyenv/pyenv)

Clone this repository
```bash
git clone git@github.com:BIGmama-technology/Hyko-sdk.git
cd Hyko-sdk
```

Run setup script
```bash
make setup
```
