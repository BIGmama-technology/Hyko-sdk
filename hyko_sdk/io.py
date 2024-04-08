import asyncio
import io
import os
from typing import Any, Optional, Self
from uuid import UUID, uuid4

import aiofiles
import httpx
import numpy as np
import soundfile  # type: ignore
from fastapi import HTTPException, status
from numpy.typing import NDArray
from PIL import Image as PIL_Image
from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from .models import Ext, StorageConfig, extension_to_mimetype


class HykoBaseType:
    file_name: str

    def __init__(
        self,
        obj_ext: Ext,
        file_name: Optional[str] = None,
    ):
        if not file_name:
            obj_id = uuid4()
            file_name = str(obj_id) + "." + obj_ext.value

        self.file_name = file_name

        self.client = httpx.AsyncClient(
            base_url=f"http://{StorageConfig.host}",
            verify=False,
            cookies={
                "access_token": f"Bearer {StorageConfig.access_token}",
                "refresh_token": f"Bearer {StorageConfig.refresh_token}",
            },
            timeout=10,
        )

    @staticmethod
    def validate_object(val: Any) -> Any:
        ...

    @staticmethod
    def validate_file_name(file_name: str) -> Any:
        ...

    def get_name(self) -> str:
        return self.file_name

    async def save(self, obj_data: bytes) -> None:
        """Save obj to file system."""
        _, ext = os.path.splitext(self.file_name)

        file_tuple = (self.file_name, obj_data, extension_to_mimetype[ext.lstrip(".")])

        res = await self.client.post(url="/storage/", files={"file": file_tuple})
        if not res.is_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"failed to write to storage. {res.text}",
            )

        self.file_name = res.json()

    async def init_from_val(self, val: bytes):
        await self.save(val)
        return self

    async def get_data(self) -> bytes:
        """read from file system"""
        res = await self.client.get(url=f"/storage/{self.file_name}")

        if not res.is_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"failed to read from storage. {res.text}",
            )

        return res.content

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema["type"] = cls.__name__.lower()

        return json_schema

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source: Self,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        json_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate_file_name),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls.get_name
            ),
        )

        python_schema = core_schema.union_schema(
            [
                json_schema,
                core_schema.no_info_plain_validator_function(cls.validate_object),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls.get_name
            ),
        )
        return core_schema.json_or_python_schema(
            json_schema=json_schema,
            python_schema=python_schema,
        )


class Image(HykoBaseType):
    @staticmethod
    def validate_object(val: "Image"):
        file_name = val.file_name
        obj_id, obj_ext = os.path.splitext(file_name)
        obj_id = UUID(obj_id)
        obj_ext = Ext(obj_ext.lstrip("."))
        assert obj_ext.value in [
            Ext.PNG,
            Ext.JPEG,
            Ext.MPEG,
            Ext.TIFF,
            Ext.TIF,
            Ext.BMP,
            Ext.JP2,
            Ext.DIB,
            Ext.PGM,
            Ext.PPM,
            Ext.PNM,
            Ext.RAS,
            Ext.HDR,
            Ext.WEBP,
            Ext.JPG,
        ], "Invalid file extension for Image error"
        return Image(obj_ext=obj_ext, file_name=file_name)

    @staticmethod
    def validate_file_name(file_name: str):
        obj_id, obj_ext = os.path.splitext(file_name)
        obj_id = UUID(obj_id)
        obj_ext = Ext(obj_ext.lstrip("."))
        assert obj_ext.value in [
            Ext.PNG,
            Ext.JPEG,
            Ext.MPEG,
            Ext.TIFF,
            Ext.TIF,
            Ext.BMP,
            Ext.JP2,
            Ext.DIB,
            Ext.PGM,
            Ext.PPM,
            Ext.PNM,
            Ext.RAS,
            Ext.HDR,
            Ext.WEBP,
            Ext.JPG,
        ], "Invalid file extension for Image error"
        return Image(obj_ext=obj_ext, file_name=file_name)

    @staticmethod
    async def from_ndarray(
        arr: np.ndarray[Any, Any],
        encoding: Ext = Ext.PNG,
    ) -> "Image":
        file = io.BytesIO()
        img = PIL_Image.fromarray(arr)  # type: ignore
        img.save(file, format=encoding.value)

        return await Image(
            obj_ext=encoding,
        ).init_from_val(
            val=file.getbuffer().tobytes(),
        )

    @staticmethod
    async def from_pil(
        img: PIL_Image.Image,
        encoding: Ext = Ext.PNG,
    ) -> "Image":
        file = io.BytesIO()
        img.save(file, format=encoding.value)

        return await Image(
            obj_ext=encoding,
        ).init_from_val(
            val=file.getbuffer().tobytes(),
        )

    async def to_ndarray(self, keep_alpha_if_png: bool = False) -> NDArray[Any]:
        data = await self.get_data()
        img_bytes_io = io.BytesIO(data)
        img = PIL_Image.open(img_bytes_io)
        img = np.asarray(img)
        if keep_alpha_if_png:
            return img
        return img[..., :3]

    async def to_pil(self) -> PIL_Image.Image:
        data = await self.get_data()
        img_bytes_io = io.BytesIO(data)
        img = PIL_Image.open(img_bytes_io)
        return img


class Audio(HykoBaseType):
    @staticmethod
    def validate_object(val: "Audio"):
        file_name = val.file_name
        obj_id, obj_ext = os.path.splitext(file_name)
        obj_id = UUID(obj_id)
        obj_ext = Ext(obj_ext.lstrip("."))
        assert obj_ext.value in [
            Ext.MP3,
            Ext.WEBM,
            Ext.WAV,
        ], "Invalid file extension for Audio error"
        return Audio(obj_ext=obj_ext, file_name=file_name)

    @staticmethod
    def validate_file_name(file_name: str):
        obj_id, obj_ext = os.path.splitext(file_name)
        obj_id = UUID(obj_id)
        obj_ext = Ext(obj_ext.lstrip("."))
        assert obj_ext.value in [
            Ext.MP3,
            Ext.WEBM,
            Ext.WAV,
        ], "Invalid file extension for Audio error"
        return Audio(obj_ext=obj_ext, file_name=file_name)

    @staticmethod
    async def from_ndarray(arr: np.ndarray[Any, Any], sampling_rate: int) -> "Audio":
        file = io.BytesIO()
        soundfile.write(file, arr, samplerate=sampling_rate, format="MP3")  # type: ignore

        return await Audio(
            obj_ext=Ext.MP3,
        ).init_from_val(
            val=file.getbuffer().tobytes(),
        )

    async def convert_to(self, new_ext: Ext):
        async with aiofiles.open(self.file_name, mode="wb") as file:
            await file.write(await self.get_data())

        out = "audio_converted." + new_ext.value

        # Run ffmpeg command asynchronously
        process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-i",
            self.file_name,
            out,
            "-y",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()

        async with aiofiles.open(out, mode="rb") as f:
            data = await f.read()

        os.remove(self.file_name)
        os.remove(out)

        return await Audio(
            obj_ext=new_ext,
        ).init_from_val(val=data)

    async def to_ndarray(  # type: ignore
        self,
        frame_offset: int = 0,
        num_frames: int = -1,
    ):
        new_audio = await self.convert_to(Ext.MP3)
        data = await new_audio.get_data()
        audio_readable = io.BytesIO(data)

        with soundfile.SoundFile(audio_readable, "r") as file_:
            frames = file_._prepare_read(frame_offset, None, num_frames)  # type: ignore
            waveform: np.ndarray = file_.read(frames, "float32", always_2d=True)  # type: ignore
            sample_rate: int = file_.samplerate

        return waveform, sample_rate  # type: ignore


class Video(HykoBaseType):
    @staticmethod
    def validate_object(val: "Video"):
        file_name = val.file_name
        obj_id, obj_ext = os.path.splitext(file_name)
        obj_id = UUID(obj_id)
        obj_ext = Ext(obj_ext.lstrip("."))
        assert obj_ext.value in [
            Ext.MP4,
            Ext.WEBM,
            Ext.AVI,
            Ext.MKV,
            Ext.MOV,
            Ext.WMV,
            Ext.GIF,
        ], "Invalid file extension for Video error"
        return Video(obj_ext=obj_ext, file_name=file_name)

    @staticmethod
    def validate_file_name(file_name: str):
        obj_id, obj_ext = os.path.splitext(file_name)
        obj_id = UUID(obj_id)
        obj_ext = Ext(obj_ext.lstrip("."))
        assert obj_ext.value in [
            Ext.MP4,
            Ext.WEBM,
            Ext.AVI,
            Ext.MKV,
            Ext.MOV,
            Ext.WMV,
            Ext.GIF,
        ], "Invalid file extension for Video error"
        return Video(obj_ext=obj_ext, file_name=file_name)


class PDF(HykoBaseType):
    @staticmethod
    def validate_object(val: "PDF"):
        file_name = val.file_name
        obj_id, obj_ext = os.path.splitext(file_name)
        obj_id = UUID(obj_id)
        obj_ext = Ext(obj_ext.lstrip("."))
        assert obj_ext.value in [Ext.PDF], "Invalid file extension for PDF error"
        return PDF(obj_ext=obj_ext, file_name=file_name)

    @staticmethod
    def validate_file_name(file_name: str):
        obj_id, obj_ext = os.path.splitext(file_name)
        obj_id = UUID(obj_id)
        obj_ext = Ext(obj_ext.lstrip("."))
        assert obj_ext.value in [Ext.PDF], "Invalid file extension for PDF error"
        return PDF(obj_ext=obj_ext, file_name=file_name)
