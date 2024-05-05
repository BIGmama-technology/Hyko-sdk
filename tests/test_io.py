from typing import Any
from unittest import mock

import numpy as np
import pytest
from PIL import Image as PIL_Image

from hyko_sdk.components import Ext
from hyko_sdk.io import PDF, Audio, Image, Video


############## Image Tests #####################
@pytest.mark.parametrize(
    "name",
    [
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.png",
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.jpg",
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.jpeg",
    ],
)
def test_validate_img_object(name: str):
    img = Image(file_name=name, obj_ext=Ext.PNG)
    validated_img = Image.validate_object(img)
    assert isinstance(validated_img, Image)
    assert validated_img.file_name == img.file_name


@pytest.mark.parametrize(
    "name",
    [
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.png",
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.jpeg",
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.jpg",
    ],
)
def test_validate_img_name(name: str):
    validated_img = Image.validate_file_name(name)
    assert isinstance(validated_img, Image)


@pytest.mark.parametrize(
    "name",
    [
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.pdf",
        "invalid_uuid.png",
    ],
)
def test_validate_img_name_with_invalid_name(name: str):
    with pytest.raises((AssertionError, ValueError)):
        Image.validate_file_name(name)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "encoding",
    [
        Ext.PNG,
        Ext.JPEG,
    ],
)
async def test_img_from_nd_array(
    mock_post_success: mock.MagicMock,
    sample_nd_array_data: np.ndarray[Any, Any],
    encoding: Ext,
):
    nd_img = await Image.from_ndarray(sample_nd_array_data, encoding)
    assert isinstance(nd_img, Image)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "encoding",
    [
        Ext.PNG,
        Ext.JPEG,
    ],
)
async def test_img_from_pil(
    mock_post_success: mock.MagicMock,
    sample_pil_image_data: PIL_Image.Image,
    encoding: Ext,
):
    pil_img = await Image.from_pil(sample_pil_image_data, encoding)
    assert isinstance(pil_img, Image)


@pytest.mark.asyncio
async def test_to_ndarray(
    mock_post_success: mock.MagicMock,
    mock_get_png: mock.MagicMock,
):
    img = await Image.from_ndarray(np.zeros((100, 100, 3), dtype=np.uint8))
    assert isinstance(await img.to_ndarray(), np.ndarray)


@pytest.mark.asyncio
async def test_to_pil(
    mock_post_success: mock.MagicMock,
    mock_get_png: mock.MagicMock,
):
    img = await Image.from_ndarray(np.zeros((100, 100, 3), dtype=np.uint8))
    assert isinstance(await img.to_pil(), PIL_Image.Image)


# ############### Audio Tests ##################3333
@pytest.mark.parametrize(
    "name, encoding",
    [
        ("7a5ab22a-68ce-11ec-83d7-0242ac130002.mp3", Ext.MP3),
        ("7a5ab22a-68ce-11ec-83d7-0242ac130002.webm", Ext.WEBM),
        ("7a5ab22a-68ce-11ec-83d7-0242ac130002.wav", Ext.WAV),
    ],
)
def test_validate_audio_object(name: str, encoding: Ext):
    audio = Audio(file_name=name, obj_ext=encoding)
    validated_audio = Audio.validate_object(audio)
    assert isinstance(validated_audio, Audio)
    assert validated_audio.file_name == audio.file_name


@pytest.mark.parametrize(
    "name",
    [
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.mp3",
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.webm",
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.wav",
    ],
)
def test_validate_audio_name(name: str):
    validated_audio = Audio.validate_file_name(name)
    assert isinstance(validated_audio, Audio)


@pytest.mark.parametrize(
    "name",
    [
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.png",
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.pdf",
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.txt",
    ],
)
def test_validate_audio_name_with_invalid_name(name: str):
    with pytest.raises(AssertionError):
        Audio.validate_file_name(name)


@pytest.mark.asyncio
async def test_audio_from_nd_array(
    sample_audio_data: np.ndarray[Any, Any],
    mock_post_success: mock.MagicMock,
):
    nd_audio = await Audio.from_ndarray(sample_audio_data, 16000)
    assert isinstance(nd_audio, Audio)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name, encoding, new_ext",
    [
        ("7a5ab22a-68ce-11ec-83d7-0242ac130002.wav", Ext.WAV, Ext.MP3),
        ("7a5ab22a-68ce-11ec-83d7-0242ac130002.mp3", Ext.MP3, Ext.WAV),
        ("7a5ab22a-68ce-11ec-83d7-0242ac130002.webm", Ext.WEBM, Ext.MP3),
    ],
)
async def test_audio_convert(
    name: str,
    encoding: Ext,
    new_ext: Ext,
    sample_audio_data: np.ndarray[Any, Any],
    mock_get_audio: mock.MagicMock,
    mock_post_success: mock.MagicMock,
):
    audio = await Audio(file_name=name, obj_ext=encoding).init_from_val(
        val=sample_audio_data.tobytes()
    )
    assert isinstance(await audio.convert_to(new_ext), Audio)  # type: ignore


############### Video Tests ##################
@pytest.mark.parametrize(
    "name, encoding",
    [
        ("7a5ab22a-68ce-11ec-83d7-0242ac130002.mp4", Ext.MP4),
        ("7a5ab22a-68ce-11ec-83d7-0242ac130002.webm", Ext.WEBM),
        ("7a5ab22a-68ce-11ec-83d7-0242ac130002.avi", Ext.AVI),
    ],
)
def test_validate_video_object(name: str, encoding: Ext):
    video = Video(file_name=name, obj_ext=encoding)
    validated_video = Video.validate_object(video)
    assert isinstance(validated_video, Video)
    assert validated_video.file_name == video.file_name


@pytest.mark.parametrize(
    "name",
    [
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.mp4",
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.webm",
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.avi",
    ],
)
def test_validate_video_name(name: str):
    validated_video = Video.validate_file_name(name)
    assert isinstance(validated_video, Video)


@pytest.mark.parametrize(
    "name",
    [
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.png",
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.pdf",
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.txt",
    ],
)
def test_validate_video_name_with_invalid_name(name: str):
    with pytest.raises(AssertionError):
        Video.validate_file_name(name)


########## PDF Tests ######################
@pytest.mark.parametrize(
    "name, encoding",
    [
        ("7a5ab22a-68ce-11ec-83d7-0242ac130002.pdf", Ext.PDF),
    ],
)
def test_validate_pdf_object(name: str, encoding: Ext):
    pdf = PDF(file_name=name, obj_ext=encoding)
    validated_pdf = PDF.validate_object(pdf)
    assert isinstance(validated_pdf, PDF)
    assert validated_pdf.file_name == pdf.file_name


@pytest.mark.parametrize(
    "name",
    [
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.pdf",
    ],
)
def test_validate_pdf_name(name: str):
    validated_pdf = PDF.validate_file_name(name)
    assert isinstance(validated_pdf, PDF)


@pytest.mark.parametrize(
    "name",
    [
        "7a5ab22a-68ce-11ec-83d7-0242ac130002.png",
    ],
)
def test_validate_pdf_name_with_invalid_name(name: str):
    with pytest.raises(AssertionError):
        PDF.validate_file_name(name)
