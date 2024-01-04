from pydantic import BaseModel, Field, validator
from fastapi import APIRouter, Request
from typing import List


class ReadQSPI(BaseModel):
    device: str
    size: int = Field(default=1)

    @validator("size")
    def size_is_not_100(cls, size):
        if size > 100:
            return 100
        return size


class WriteQSPI(BaseModel):
    device: str
    data: List[int] = Field(default_factory=list)

    @validator("data")
    def data_is_ubyte(cls, data: [int]):
        if max(data) > 256:
            raise ValueError("item in data overflows ubyte range")
        return data


class SpyQSPI(BaseModel):
    device: str
    nSamples: int = Field(default=2)

    @validator("nSamples")
    def size_is_not_100(cls, size):
        if size > 100:
            return 100
        return size


router = APIRouter()


@router.post("/read")
def read_qspi(Request: Request, data: ReadQSPI) -> {}:
    manager = Request.app.state.manager
    future_result = manager.read_qspi(data.device, data.size)
    return future_result.result()


@router.post("/write")
async def write_qspi(Request: Request, data: WriteQSPI) -> {}:
    manager = Request.app.state.manager
    future_result = manager.write_qspi(data.device, len(data.data), data.data)
    return future_result.result()


@router.post("/spy")
def spy_qspi(Request: Request, data: SpyQSPI) -> {}:
    manager = Request.app.state.manager
    future_result = manager.spy_qspi(data.device, data.nSamples)
    return future_result.result()
