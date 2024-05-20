from typing import Any, Callable, Coroutine, Type, TypeVar

from pydantic import BaseModel

from hyko_sdk.models import StorageConfig

from .models import (
    APIMetaData,
    Category,
    CoreModel,
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
        self.inputs_model = CoreModel
        self.params_model = CoreModel

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

    def on_call(self, f: OnCallType[...]):
        self.call_ = f

    def call(
        self,
        inputs: dict[str, Any],
        params: dict[str, Any],
        storage_config: StorageConfig,
    ):
        StorageConfig.configure(**storage_config.model_dump())
        validated_inputs = self.inputs_model(**inputs)
        validated_params = self.params_model(**params)

        return self.call_(validated_inputs, validated_params)

    def dump_metadata(self) -> str:
        metadata = MetaDataBase(
            **self.get_base_metadata().model_dump(exclude_none=True)
        )
        return metadata.model_dump_json(
            exclude_none=True,
            by_alias=True,
        )


class ToolkitAPI(ToolkitBase):
    def __init__(self, name: str, task: str, description: str):
        super().__init__(name=name, task=task, desc=description)
        self.category = Category.API

    def get_metadata(self) -> APIMetaData:
        return APIMetaData(**self.get_base_metadata().model_dump(exclude_none=True))


class ToolkitUtils(ToolkitAPI):
    def __init__(self, name: str, task: str, description: str):
        super().__init__(name=name, task=task, description=description)
        self.category = Category.UTILS

    def get_metadata(self) -> UtilsMetaData:
        return UtilsMetaData(**self.get_base_metadata().model_dump(exclude_none=True))


class ToolkitFunction(ToolkitBase):
    def __init__(
        self,
        name: str,
        task: str,
        desc: str,
    ):
        super().__init__(name=name, task=task, desc=desc)
        self.category = Category.FUNCTION

    def get_metadata(self) -> FunctionMetaData:
        return FunctionMetaData(
            **self.get_base_metadata().model_dump(exclude_none=True)
        )


class ToolkitModel(ToolkitFunction):
    def __init__(
        self,
        name: str,
        task: str,
        desc: str,
    ):
        super().__init__(name=name, task=task, desc=desc)
        self.category = Category.MODEL
        self.started: bool = False

    def on_startup(self, f: OnStartupFuncType[BaseModel]):
        self.startup_ = f

    def startup(self, params: dict[str, Any]):
        validated_params = self.params_model(**params)
        return self.startup_(validated_params)

    def get_metadata(self) -> ModelMetaData:
        return ModelMetaData(**self.get_base_metadata().model_dump(exclude_none=True))
