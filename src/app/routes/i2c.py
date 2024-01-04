from typing import List
from pydantic import BaseModel,validator, Field
from fastapi import APIRouter, Request


router = APIRouter()


class WriteI2C(BaseModel):
    device:str
    data: List[int] = Field(default_factory=list)
    address: int = Field(default=0x1D)
    @validator("data")
    def data_is_ubyte(cls,data:[int]):
        if max(data) >256:
            raise ValueError("item in data overflows ubyte range")
        return data
    @validator("address")
    def address_is_ubyte(cls,address:int):
        if address >255:
            raise ValueError("address is not in ubyte range")
        return address

    
class ReadI2C(BaseModel):
    device:str
    size:int = Field(default= 1)
    address:int =Field(default=0x1D)
    @validator("address")
    def address_is_ubyte(cls,address:int):
        if address >255:
            raise ValueError("address is not in ubyte range")
    @validator("size")
    def size_is_not_100(cls,size):
        if size >100:
            return 100
        return size

class SpyI2C(BaseModel):
    device:str
    nTransactions:int | None
    @validator("nTransactions", always=True)
    def nTransactions_default_value(cls,nTransactions):
        if nTransactions > 0:
            return nTransactions
        return 1
        
    
    
@router.post("/read")
def read_i2c(Request: Request, data:ReadI2C) -> {}:
    print(data.size)
    manager = Request.app.state.manager
    future_result = manager.read_i2c(data.device, data.size,data.address)
    return future_result.result()


@router.post("/write")
async def write_i2c(Request: Request, data:WriteI2C) -> {}:
    manager = Request.app.state.manager
    future_result = manager.write_i2c(data.device, len(data.data), data.data, data.address)
    return future_result.result()


@router.post("/spy")
async def spy_i2c(
    Request: Request, data:SpyI2C
) -> {}:
    manager = Request.app.state.manager
    future_result = manager.spy_i2c(data.device, data.nTransactions)
    return future_result.result()
