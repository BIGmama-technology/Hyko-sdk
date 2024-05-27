from typing import Any, Callable, Coroutine, Optional, Type, TypeVar

from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema

from .json_schema import (
    CustomJsonSchema,
    JsonSchemaGenerator,
    JsonSchemaGeneratorWithComponents,
)
from .models import (
    Category,
    CoreModel,
    FieldMetadata,
    Icon,
    MetaDataBase,
    StorageConfig,
)

InputsType = TypeVar("InputsType", bound="BaseModel")
ParamsType = TypeVar("ParamsType", bound="BaseModel")
OutputsType = TypeVar("OutputsType", bound="BaseModel")

OnStartupFuncType = Callable[[ParamsType], Coroutine[Any, Any, None]]
OnShutdownFuncType = Callable[[], Coroutine[Any, Any, None]]
OnExecuteFuncType = Callable[[InputsType, ParamsType], Coroutine[Any, Any, OutputsType]]
OnCallType = Callable[..., Coroutine[Any, Any, OutputsType]]

T = TypeVar("T", bound=Type[BaseModel])


class ToolkitNode:
    def __init__(
        self,
        name: str,
        task: str,
        description: str,
        cost: int,
        category: Category,
        icon: Optional[Icon] = None,
    ):
        self.category = category
        self.description = description
        self.name = name
        self.task = task
        self.cost = cost
        self.icon = icon
        self.inputs = {}
        self.outputs = {}
        self.params = {}
        self.inputs_model = CoreModel
        self.params_model = CoreModel

    def fields_to_metadata(
        self,
        model: Type[BaseModel],
        schema_generator: type[GenerateJsonSchema] = JsonSchemaGeneratorWithComponents,
    ):
        schema = CustomJsonSchema.model_validate(
            model.model_json_schema(
                schema_generator=schema_generator,
                ref_template="{model}",
            )
        )
        return {
            field: FieldMetadata(
                name=field,
                **prop.model_dump(),
            )
            for field, prop in schema.properties.items()
        }

    def set_input(self, model: T) -> T:
        self.inputs = self.fields_to_metadata(model)
        self.inputs_model = model
        return model

    def set_output(self, model: T) -> T:
        self.outputs = self.fields_to_metadata(
            model, schema_generator=JsonSchemaGenerator
        )
        return model

    def set_param(self, model: T) -> T:
        self.params = self.fields_to_metadata(model)
        self.params_model = model
        return model

    def get_metadata(self):
        return MetaDataBase(
            category=self.category,
            name=self.name,
            task=self.task,
            description=self.description,
            inputs=self.inputs,
            params=self.params,
            outputs=self.outputs,
            cost=self.cost,
            icon=self.icon,
        )

    def on_call(self, f: OnCallType[...]):
        self._call = f

    async def call(
        self,
        inputs: dict[str, Any],
        params: dict[str, Any],
        storage_config: StorageConfig,
    ):
        StorageConfig.configure(**storage_config.model_dump())
        validated_inputs = self.inputs_model(**inputs)
        validated_params = self.params_model(**params)

        return await self._call(validated_inputs, validated_params)

    def dump_metadata(self) -> str:
        metadata = self.get_metadata()
        return metadata.model_dump_json(exclude_none=True)


class ToolkitModel(ToolkitNode):
    def __init__(
        self,
        name: str,
        task: str,
        description: str,
        cost: int,
        category: Category = Category.MODEL,
    ):
        super().__init__(
            name=name,
            task=task,
            description=description,
            cost=cost,
            category=category,
            icon="models",
        )
        self.started: bool = False
        self._startup = None

    def on_startup(self, f: OnStartupFuncType[...]):
        self._startup = f

    async def startup(self, params: dict[str, Any]):
        if self.started or not self._startup:
            return

        validated_params = self.params_model(**params)
        await self._startup(validated_params)
        self.started = True

    async def call(
        self,
        inputs: dict[str, Any],
        params: dict[str, Any],
        storage_config: StorageConfig,
    ):
        StorageConfig.configure(**storage_config.model_dump())
        validated_inputs = self.inputs_model(**inputs)
        validated_params = self.params_model(**params)
        await self.startup(params)

        return await self._call(validated_inputs, validated_params)
