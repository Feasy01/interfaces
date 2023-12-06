from typing import Annotated
from ctypes import *

from fastapi import APIRouter, Request, Body


router = APIRouter()


@router.post("/read/{device}")
def read_can(Request: Request, device: str, size: Annotated[int, Body()]) -> {}:
    manager = Request.app.state.manager
    result = manager.read_can(device, size)
    # print(manager.dut)
    return result.result()


@router.post("/write/{device}")
async def write_can(
    Request: Request, device: str, data: Annotated[bytes, Body()]
) -> {}:
    manager = Request.app.state.manager
    result = manager.write_can(device, data)
    return result.result()
