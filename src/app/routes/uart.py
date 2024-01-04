from pydantic import BaseModel, Field, validator
from fastapi import APIRouter, Request
from typing import List

class ReadUART(BaseModel):
    device: str
    size: int = Field(default=1)
    time: int = Field(default=10)

    @validator("size")
    def size_less_than_1000(cls, size):
        if size > 1000:
            return 1000
        return size

    @validator("time")
    def time_is_sensible(cls, time):
        if time < 1 or time > 120:
            raise ValueError("please provide a sensible timeframe for the measurement")
        return time


class WriteUART(BaseModel):
    device: str
    data: List[int] | str = Field(default_factory=list)

    @validator("data")
    def data_is_str_or_ubyte(cls, data):
        if not isinstance(data, str) or max(data) < 255:
            raise ValueError("data is neither a string nor a ubyte array")
        return data


router = APIRouter()


@router.post("/read")
def read_uart(Request: Request, data: ReadUART) -> {}:
    manager = Request.app.state.manage
    future_result = manager.read_uart(data.device, data.size, data.time)
    return future_result.result()


@router.post("/write")
async def write_uart(Request: Request, data: WriteUART) -> {}:
    manager = Request.app.state.manager
    future_result = manager.write_uart(data.device, data.data)
    return future_result.result()
