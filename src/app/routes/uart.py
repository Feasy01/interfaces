import time
from enum import Enum
from typing import List, Optional, Annotated
from ctypes import *

from fastapi import APIRouter, Request, Body


router = APIRouter()


@router.post("/read/{device}")
def read_uart(Request: Request, device: str, size: Annotated[int, Body()]) -> {}:
    manager = Request.app.state.manager
    result = manager.read_uart(device, size)
    # print(manager.dut)
    return result.result()


@router.post("/write/{device}")
async def write_uart(
    Request: Request, device: str, data: Annotated[bytes, Body()]
) -> {}:
    manager = Request.app.state.manager
    result = manager.write_uart(device, data)
    return result.result()
