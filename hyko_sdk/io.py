import io
import os
from typing import Any, Optional, Self
from uuid import UUID, uuid4

import httpx
import numpy as np
import soundfile  # type: ignore
from numpy.typing import NDArray
from PIL import Image as PIL_Image
from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from .models import Ext


class StorageConfig:
    access_token: str
    refresh_token: str
    host: str

    @classmethod
    def configure(cls, access_token: str, refresh_token: str, host: str):
        cls.access_token = access_token
        cls.refresh_token = refresh_token
        cls.host = host


class HykoBaseType:
    file_name: str

    def __init__(
        self,
        obj_ext: Ext,
        file_name: Optional[str] = None,
        val: Optional[bytes] = None,
    ):
        if not file_name:
            obj_id = uuid4()
            file_name = str(obj_id) + "." + obj_ext.value

        self.file_name = file_name

        self.client = httpx.Client(
            base_url=f"https://{StorageConfig.host}",
            verify=False if StorageConfig.host == "api.traefik.me" else True,
            cookies={
                "access_token": f"Bearer {StorageConfig.access_token}",
                "refresh_token": f"Bearer {StorageConfig.refresh_token}",
            },
        )

        if val:
            self.save(val)

    @staticmethod
    def validate_object(val: Any) -> Any:
        ...

    @staticmethod
    def validate_file_name(file_name: str) -> Any:
        ...

    def get_name(self) -> str:
        return self.file_name

    def save(self, obj_data: bytes) -> None:
        """Save obj to file system."""

        file_tuple = (self.file_name, obj_data, "application/octet-stream")

        self.client.post(url="/storage", files={"file": file_tuple})

    def get_data(self) -> bytes:
        """read from file system"""
        res = self.client.get(url=f"/storage/{self.file_name}")

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
    def from_ndarray(
        arr: np.ndarray[Any, Any],
        encoding: Ext = Ext.PNG,
    ) -> "Image":
        file = io.BytesIO()
        img = PIL_Image.fromarray(arr)  # type: ignore
        img.save(file, format=encoding.value)

        return Image(
            val=file.getbuffer().tobytes(),
            obj_ext=encoding,
        )

    @staticmethod
    def from_pil(
        img: PIL_Image.Image,
        encoding: Ext = Ext.PNG,
    ) -> "Image":
        file = io.BytesIO()
        img.save(file, format=encoding.value)

        return Image(
            val=file.getbuffer().tobytes(),
            obj_ext=encoding,
        )

    def to_ndarray(self, keep_alpha_if_png: bool = False) -> NDArray[Any]:
        if self.get_data():
            img_bytes_io = io.BytesIO(self.get_data())
            img = PIL_Image.open(img_bytes_io)
            img = np.asarray(img)
            if keep_alpha_if_png:
                return img
            return img[..., :3]
        else:
            raise RuntimeError("Image decode error (Image data not loaded)")

    def to_pil(self) -> PIL_Image.Image:
        img_bytes_io = io.BytesIO(self.get_data())
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
    def from_ndarray(arr: np.ndarray[Any, Any], sampling_rate: int) -> "Audio":
        file = io.BytesIO()
        soundfile.write(file, arr, samplerate=sampling_rate, format="MP3")  # type: ignore
        return Audio(
            val=file.getbuffer().tobytes(),
            obj_ext=Ext.MP3,
        )

    def convert_to(self, new_ext: Ext) -> HykoBaseType:
        raise NotImplementedError

    def to_ndarray(  # type: ignore
        self,
        frame_offset: int = 0,
        num_frames: int = -1,
    ):
        new_audio = self.convert_to(Ext.MP3)

        audio_readable = io.BytesIO(new_audio.get_data())

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
