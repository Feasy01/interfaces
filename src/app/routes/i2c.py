import time
from enum import Enum
from typing import List, Optional, Annotated
from ctypes import *
from pydantic import BaseModel

from fastapi import APIRouter, Request, Body


router = APIRouter()


class WriteI2C(BaseModel):
    data: bytes
    address: bytes


@router.post("/read/{device}")
def read_i2c(Request: Request, device: str, size: int) -> {}:
    print(size)
    manager = Request.app.state.manager
    print(device, size)
    result = manager.read_i2c(device, size)
    # print(manager.dut)
    return result.result()


@router.post("/write/{device}")
async def write_i2c(Request: Request, device: str, unicode: WriteI2C) -> {}:
    manager = Request.app.state.manager
    # data = bytes(unicode.data, encoding="raw_unicode_escape")
    # address = bytes(unicode.address, encoding="raw_unicode_escape")
    help = (c_ubyte * len(unicode.data))(*unicode.data)
    print(list(help))
    c = bytes.fromhex(unicode.data)
    print(c)
    a = int.from_bytes(unicode.data, byteorder="little")
    print(a)
    print(unicode.data, unicode.address)
    # result = manager.write_i2c(device, len(data), data, address)
    return unicode


@router.post("/spy/{device}")
async def spy_i2c(
    Request: Request, device: str, nsamples: Annotated[int, Body()]
) -> {}:
    manager = Request.app.state.manager
    result = manager.spy_i2c(device, nsamples)
    # print(manager.dut)
    return result.result()
