from typing import List
from pydantic import BaseModel, Field, validator
from fastapi import APIRouter, Request


class WriteSPI(BaseModel):
    device: str
    data: List[int] = Field(default_factory=list)

    @validator("data")
    def data_is_ubyte(cls, data):
        if max(data) > 255:
            raise ValueError("data is not in ubyte range")
        return data


class ReadSPI(BaseModel):
    device: str
    size: int = Field(default=1)

    @validator("size")
    def size_less_than_1000(cls, size):
        return size if size < 1000 else 1000


class SpySPI(BaseModel):
    device: str
    nSamples: int = Field(default=1)

    @validator("nSamples")
    def nsamples_less_than_50(cls, nSamples):
        return nSamples if nSamples < 50 else 50


router = APIRouter()


@router.post("/read")
def read_spi(Request: Request, data: ReadSPI) -> {}:
    manager = Request.app.state.manager
    future_result = manager.read_spi(data.device, data.size)
    return future_result.result()


@router.post("/write")
async def write_spi(Request: Request, data: WriteSPI) -> {}:
    manager = Request.app.state.manager
    future_result = manager.write_spi(data.device, len(data.data), data.data)
    return future_result.result()


@router.post("/spy")
def spy_spi(Request: Request, data: SpySPI) -> {}:
    manager = Request.app.state.manager
    future_result = manager.spy_spi(data.device, data.nsamples)
    return future_result.result()
