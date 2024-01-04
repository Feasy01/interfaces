from typing import List
from pydantic import BaseModel, validator, Field

from fastapi import APIRouter, Request, HTTPException


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
    devices: List[str] = Field(default_factory=list)
    period_ms: int = Field(default=200)
    sample_rate: int = Field(default=100000)
    rising_edge: List[int] | None = Field(default_factory=list)
    falling_edge: List[int] | None = Field(default_factory=list)

    @validator("rising_edge")
    def rising_edge_contents_in_devices_range(cls, rising_edge, values):
        if min(rising_edge) >= 0 and max(rising_edge) < len(values["devices"]):
            raise ValueError("rising_edge out of range")
        return rising_edge

    @validator("falling_edge")
    def falling_edge_contents_in_devices_range(cls, falling_edge, values):
        if not (min(falling_edge) >= 0 and max(falling_edge) < len(values["devices"])):
            raise ValueError("falling_edge out of range")
        return falling_edge

    @validator("period_ms")
    def period_ms_not_negative(cls, period_ms):
        if not period_ms > 0:
            raise ValueError
        return period_ms

    @validator("sample_rate")
    def sample_rate_not_negative(cls, sample_rate):
        if not sample_rate > 0:
            raise ValueError
        return sample_rate


@router.post("/record_multiple")
async def record_gpio(Request: Request, data: RecordGpio) -> List[int]:
    manager = Request.app.state.manager
    print(data)
    result = manager.record_gpio(
        data.devices,
        data.period_ms,
        data.sample_rate,
        data.rising_edge,
        data.falling_edge,
    )
    if isinstance(response := result.result(), Exception):
        raise HTTPException(
            status_code=400, detail=f"{response.__class__.__name__}:{str(response)}"
        )
    return response
