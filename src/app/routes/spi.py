import time
from enum import Enum
from typing import List, Optional, Annotated
from ctypes import *

from fastapi import APIRouter, Request, Body


router = APIRouter()


@router.post("/read/{device}")
def read_spi(Request: Request, device: str, size: Annotated[int, Body()]) -> {}:
    manager = Request.app.state.manager
    result = manager.read_spi(device, size)
    # print(manager.dut)
    return result.result()


@router.post("/write/{device}")
async def write_spi(
    Request: Request, device: str, data: Annotated[bytes, Body()]
) -> {}:
    manager = Request.app.state.manager
    result = manager.write_spi(device, len(data), data)
    return result.result()


@router.post("/spy/{device}")
def spy_spi(Request: Request, device: str, nsamples: Annotated[int, Body()]) -> {}:
    manager = Request.app.state.manager
    result = manager.spy_spi(device, nsamples)
    # print(manager.dut)
    return result.result()
