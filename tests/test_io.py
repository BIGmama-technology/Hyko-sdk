from typing import Any
from unittest import mock

import numpy as np
import pytest
from PIL import Image as PIL_Image

from hyko_sdk.components import Ext
from hyko_sdk.io import Audio, Image


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
