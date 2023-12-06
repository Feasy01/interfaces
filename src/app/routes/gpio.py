from typing import Annotated, List
from ctypes import *
from pydantic import BaseModel

from fastapi import APIRouter, Request, Body


router = APIRouter()


# @router.post("/read/{device}")
# def read_gpio(Request: Request, device: str, size: Annotated[int, Body()]) -> {}:
#     manager = Request.app.state.manager
#     result = manager.read_i2c(device, size)
#     # print(manager.dut)
#     return result.result()


# @router.post("/write/{device}")
# async def write_gpio(Request: Request, device: str, data: Annotated[bytes, Body()], address: Annotated[bytes, Body()]) -> {}:
#     manager = Request.app.state.manager
#     result = manager.write_i2c(device, len(data), data, address)
#     return result.result()
class RecordGpio(BaseModel):
    devices: List[str]
    period_ms: int
    sample_rate: int
    rising_edge: List[int]
    falling_ednge: List[int]


@router.post("/record_multiple")
async def record_gpio(Request: Request, data: RecordGpio) -> bool:
    manager = Request.app.state.manager
    result = manager.record_gpio(
        RecordGpio.devices,
        RecordGpio.period_ms,
        RecordGpio.sample_rate,
        RecordGpio.rising_edge,
        RecordGpio.falling_edge,
    )
    # print(manager.dut)
    return True
