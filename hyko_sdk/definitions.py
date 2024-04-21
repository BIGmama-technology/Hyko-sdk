import json
from typing import Any, Callable, Coroutine, Type, TypeVar

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from hyko_sdk.models import StorageConfig

from .models import (
    APIMetaData,
    Category,
    FunctionMetaData,
    HykoJsonSchema,
    MetaDataBase,
    ModelMetaData,
    UtilsMetaData,
)
from .utils import to_friendly_types

InputsType = TypeVar("InputsType", bound="BaseModel")
ParamsType = TypeVar("ParamsType", bound="BaseModel")
OutputsType = TypeVar("OutputsType", bound="BaseModel")

OnStartupFuncType = Callable[[ParamsType], Coroutine[Any, Any, None]]
OnShutdownFuncType = Callable[[], Coroutine[Any, Any, None]]
OnExecuteFuncType = Callable[[InputsType, ParamsType], Coroutine[Any, Any, OutputsType]]
OnCallType = Callable[..., Coroutine[Any, Any, OutputsType]]

T = TypeVar("T", bound=Type[BaseModel])


class ToolkitBase:
    def __init__(
        self,
        name: str,
        task: str,
        desc: str,
    ):
        self.category: Category = Category.FUNCTION
        self.desc = desc
        self.name = name
        self.task = task
        self.inputs = None
        self.outputs = None
        self.params = None

    def set_input(self, model: T) -> T:
        self.inputs = HykoJsonSchema(
            **model.model_json_schema(),
            friendly_types=to_friendly_types(model),
        )
        return model

    def set_output(self, model: T) -> T:
        self.outputs = HykoJsonSchema(
            **model.model_json_schema(),
            friendly_types=to_friendly_types(model),
        )
        return model

    def set_param(self, model: T) -> T:
        self.params = HykoJsonSchema(
            **model.model_json_schema(),
            friendly_types=to_friendly_types(model),
        )
        return model

    def get_base_metadata(self):
        return MetaDataBase(
            category=self.category,
            name=self.name,
            task=self.task,
            description=self.desc,
            inputs=self.inputs,
            params=self.params,
            outputs=self.outputs,
        )

    def dump_metadata(self) -> str:
        metadata = MetaDataBase(
            **self.get_base_metadata().model_dump(exclude_none=True)
        )
        return metadata.model_dump_json(
            exclude_none=True,
            by_alias=True,
        )


class ToolkitFunction(ToolkitBase, FastAPI):
    def __init__(
        self,
        name: str,
        task: str,
        description: str,
        absolute_dockerfile_path: str,
        docker_context: str,
    ):
        ToolkitBase.__init__(self, name, task, description)
        self.absolute_dockerfile_path = absolute_dockerfile_path
        self.docker_context = docker_context
        FastAPI.__init__(self)
        self.configure()

        self.category = Category.FUNCTION

    def configure(self):
        async def wrapper(
            storage_config: StorageConfig,
        ):
            StorageConfig.configure(**storage_config.model_dump())

        return self.post("/configure")(wrapper)

    def on_execute(self, f: OnExecuteFuncType[InputsType, ParamsType, OutputsType]):
        async def wrapper(
            inputs: InputsType,
            params: ParamsType,
        ) -> JSONResponse:
            try:
                outputs = await f(inputs, params)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=e.__repr__(),
                ) from e

            return JSONResponse(content=json.loads(outputs.model_dump_json()))

        wrapper.__annotations__["inputs"] = f.__annotations__["inputs"]
        wrapper.__annotations__["params"] = f.__annotations__["params"]

        return self.post("/execute")(wrapper)

    def dump_metadata(self) -> str:
        base_metadata = self.get_base_metadata()

        assert self.absolute_dockerfile_path, "absolute docker file path missing"
        assert self.docker_context, "docker context path missing"

        metadata = FunctionMetaData(
            **base_metadata.model_dump(exclude_none=True),
            dockerfile_path=self.absolute_dockerfile_path,
            docker_context=self.docker_context,
        )
        return metadata.model_dump_json(
            exclude_none=True,
            by_alias=True,
        )

    def get_metadata(self) -> FunctionMetaData:
        base_metadata = self.get_base_metadata()

        return FunctionMetaData(
            **base_metadata.model_dump(exclude_none=True),
            dockerfile_path=self.absolute_dockerfile_path,
            docker_context=self.docker_context,
        )


class ToolkitModel(ToolkitFunction):
    def __init__(
        self,
        name: str,
        task: str,
        description: str,
        absolute_dockerfile_path: str,
        docker_context: str,
    ):
        super().__init__(
            name=name,
            task=task,
            description=description,
            absolute_dockerfile_path=absolute_dockerfile_path,
            docker_context=docker_context,
        )
        self.category = Category.MODEL
        self.started: bool = False
        self.startup_params = None

    def set_startup_params(self, model: T) -> T:
        self.startup_params = HykoJsonSchema(
            **model.model_json_schema(),
            friendly_types=to_friendly_types(model),
        )
        return model

    def on_startup(self, f: OnStartupFuncType[ParamsType]):
        async def wrapper(startup_params: ParamsType):
            if not self.started:
                try:
                    await f(startup_params)
                    self.started = True
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=e.__repr__(),
                    ) from e

        wrapper.__annotations__ = f.__annotations__
        return self.post("/startup")(wrapper)

    def on_shutdown(self, f: OnShutdownFuncType) -> OnShutdownFuncType:
        return self.on_event("shutdown")(f)

    def dump_metadata(self) -> str:
        base_metadata = self.get_base_metadata()

        assert self.absolute_dockerfile_path, "absolute docker file path missing"
        assert self.docker_context, "docker context path missing"

        metadata = ModelMetaData(
            **base_metadata.model_dump(exclude_none=True),
            startup_params=self.startup_params,
            dockerfile_path=self.absolute_dockerfile_path,
            docker_context=self.docker_context,
        )
        return metadata.model_dump_json(exclude_none=True, by_alias=True)

    def get_metadata(self) -> ModelMetaData:
        return ModelMetaData(
            **self.get_base_metadata().model_dump(exclude_none=True),
            dockerfile_path=self.absolute_dockerfile_path,
            startup_params=self.startup_params,
            docker_context=self.docker_context,
        )


class ToolkitAPI(ToolkitBase):
    def __init__(self, name: str, task: str, description: str):
        super().__init__(name=name, task=task, desc=description)
        self.category = Category.API

    def set_input(self, model: T) -> T:
        self.inputs_model = model
        self.inputs = HykoJsonSchema(
            **model.model_json_schema(),
            friendly_types=to_friendly_types(model),
        )
        return model

    def set_param(self, model: T) -> T:
        self.params_model = model
        self.params = HykoJsonSchema(
            **model.model_json_schema(),
            friendly_types=to_friendly_types(model),
        )
        return model

    def on_call(self, f: OnCallType[...]):
        self.call = f

    def execute(
        self,
        inputs: dict[str, Any],
        params: dict[str, Any],
        storage_config: StorageConfig,
    ):
        StorageConfig.configure(**storage_config.model_dump())
        validated_inputs = self.inputs_model(**inputs)
        validated_params = self.params_model(**params)

        return self.call(validated_inputs, validated_params)

    def get_metadata(self) -> APIMetaData:
        return APIMetaData(**self.get_base_metadata().model_dump(exclude_none=True))


class ToolkitUtils(ToolkitAPI):
    def __init__(self, name: str, task: str, description: str):
        super().__init__(name=name, task=task, description=description)
        self.category = Category.UTILS

    def get_metadata(self) -> UtilsMetaData:
        return UtilsMetaData(**self.get_base_metadata().model_dump(exclude_none=True))
