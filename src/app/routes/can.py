from pydantic import BaseModel, Field, validator
from fastapi import APIRouter, Request
from typing import List 

class ReadCAN(BaseModel):
    device: str
    size: int = Field(default=8)
    @validator("size")
    def size_less_than_1000(cls,size):
        return size if size<1000 else 1000

class WriteCAN(BaseModel):
    device: str
    data: List[int] = Field(default_factory=list)
    @validator("data")
    def data_is_ubyte(cls,data:[int]):
        if max(data) >256:
            raise ValueError("item in data overflows ubyte range")
        return data

router = APIRouter()


@router.post("/read")
def read_can(Request: Request, data: ReadCAN) -> {}:
    manager = Request.app.state.manager
    result = manager.read_can(data.device, data.size)
    return result.result()


@router.post("/write")
async def write_can(Request: Request, data: WriteCAN) -> {}:
    manager = Request.app.state.manager
    result = manager.write_can(data.device, data.data)
    return result.result()
