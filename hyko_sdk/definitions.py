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
    SupportedProviders,
)

InputsType = TypeVar("InputsType", bound="BaseModel")
ParamsType = TypeVar("ParamsType", bound="BaseModel")
OutputsType = TypeVar("OutputsType", bound="BaseModel")

OnStartupFuncType = Callable[[ParamsType], Coroutine[Any, Any, None]]
OnShutdownFuncType = Callable[[], Coroutine[Any, Any, None]]
OnExecuteFuncType = Callable[[InputsType, ParamsType], Coroutine[Any, Any, OutputsType]]
OnCallType = Callable[..., Coroutine[Any, Any, OutputsType]]

T = TypeVar("T", bound=Type[BaseModel])


class Registry:
    _registry: dict[str, "ToolkitNode"] = {}
    _callbacks_registry: dict[
        str, Callable[..., Coroutine[Any, Any, MetaDataBase]]
    ] = {}

    @classmethod
    def register(cls, name: str, definition: "ToolkitNode"):
        cls._registry[name] = definition

    @classmethod
    def get_handler(cls, name: str) -> "ToolkitNode":
        if name not in cls._registry:
            raise ValueError(f"handler {name} not found")
        return cls._registry[name]

    @classmethod
    def get_all_metadata(cls):
        return [definition.get_metadata() for definition in cls._registry.values()]

    @classmethod
    def register_callback(
        cls, id: str, callback: Callable[..., Coroutine[Any, Any, MetaDataBase]]
    ):
        cls._callbacks_registry[id] = callback

    @classmethod
    def get_callback(cls, id: str):
        if id not in cls._callbacks_registry:
            raise ValueError(f"callback {id} not found")
        return cls._callbacks_registry[id]


class ToolkitNode:
    def __init__(
        self,
        name: str,
        task: str,
        description: str,
        category: Category,
        cost: int = 0,
        icon: Optional[Icon] = None,
        auth: Optional[SupportedProviders] = None,
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
        self.auth = auth

        # For models
        self.started: bool = False
        self._startup = None

        # Automatically register the instance upon creation
        Registry.register(self.get_metadata().image, self)

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
            auth=self.auth,
        )

    def on_call(self, f: OnCallType[...]):
        self._call = f

    def dump_metadata(self) -> str:
        metadata = self.get_metadata()
        return metadata.model_dump_json(exclude_none=True)

    def on_startup(self, f: OnStartupFuncType[...]):
        self._startup = f

    async def startup(self, validated_params: Any):
        if self.started or not self._startup:
            return

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

        await self.startup(validated_params)

        return await self._call(validated_inputs, validated_params)

    def callback(self, trigger: str | list[str], id: str):
        if isinstance(trigger, list):
            for item in trigger:
                field = self.params.get(item)
                assert field, "trigger field not found in params"
                field.callback_id = id
        else:
            field = self.params.get(trigger)
            assert field, "trigger field not found in params"
            field.callback_id = id

        def wrapper(
            callback: Callable[..., Coroutine[Any, Any, MetaDataBase]],
        ):
            Registry.register_callback(id, callback)
            return callback

        return wrapper
