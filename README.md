<!-- x-release-please-start-version -->
![Static Badge](https://img.shields.io/badge/Release-v4.5.0-/?style=flat&logo=track) 

![Test Badge](https://github.com/bigmama-technology/Hyko-sdk/actions/workflows/test.yml/badge.svg)
![Test Coverage](./reports/coverage-badge.svg) 
<!-- x-release-please-end -->

# Hyko python SDK
## Table of contents

- [Description](#description)
- [Definitions](#definitions)
- [Getting Started](#getting-started)

## Description 

Hyko sdk is a python package that allows you to define functions/models and APIs used inside [Hyko toolkit](https://github.com/BIGmama-technology/Hyko-toolkit).

## Definitions

In the `hyko_sdk/definitions.py` module, we encounter three fundamental base classes collectively referred to as **definitions**:

- `ToolkitFunction`: This serves as the base class for all functions within the Hyko Toolkit repository.
- `ToolkitModel`: As the base class for all models within the Hyko Toolkit repository.
- `ToolkitAPI`: Serving as the base class for all APIs within the Hyko Toolkit repository.

The primary responsibility of these classes is to define the `deploy` function, which orchestrates the process of verifying the coherence of the function and subsequently writing its metadata to the Hyko database.

Additionally, these classes introduce several decorators:

- `@set_input`, `@set_output`, and `@set_param`: These decorators annotate the Pydantic model representing the inputs, outputs, and parameters of the node, respectively.

- Specifically, `ToolkitFunction` also introduces:
  - `@on_execute`: This decorator pertains to the execution function.

- On the other hand, `ToolkitModel`, inheriting from `ToolkitFunction`, introduces:
  - `@on_startup`: This decorator concerns the startup function of the model, such as loading weights.
  - `@set_startup_params`: Decorating the Pydantic model for startup parameters.
  - `@on_shutdown`: This decorator addresses the shutdown function.

> example of usage can be found in [Hyko toolkit](https://github.com/BIGmama-technology/Hyko-toolkit)

## Getting started

1. Ensure you have Poetry and pyenv installed on your system. You can refer to the following links for installation guidance:

- [Poetry](https://python-poetry.org/docs/#installation)
- [Pyenv](https://github.com/pyenv/pyenv)

2. Clone the repository:

    ```bash
    git clone https://github.com/BIGmama-technology/Hyko-sdk.git sdk
    ```

    ```bash
    cd sdk
    ```

3. Execute the setup script to install the Python version used with the Hyko Toolkit (3.11.6) and install the required dependencies using Poetry. This script also activates the new virtual environment.

    ```bash
    make setup
    ```
