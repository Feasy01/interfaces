from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.manager.tester_manager import TesterManager
from src.utils.parsers.cfg_json_parser import CfgParserJson
from .routes import spi, dut, i2c, uart, qspi, can, gpio


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.manager = TesterManager()
    app.state.manager.set_config(
        CfgParserJson.parse_cfg("src/config/demo-setup.json")
    )
    yield
    # app.state.manager.__del__()


app = FastAPI(lifespan=lifespan)


app.include_router(
    spi.router,
    prefix="/spi",
    tags=["SPI"],
)

app.include_router(qspi.router, prefix="/qspi", tags=["QSPI"])

app.include_router(gpio.router, prefix="/gpio", tags=["GPIO"])

app.include_router(uart.router, prefix="/uart", tags=["UART"])

app.include_router(i2c.router, prefix="/i2c", tags=["I2C"])

app.include_router(can.router, prefix="/can", tags=["CAN"])

app.include_router(dut.router, prefix="/dut", tags=["DUT"])

# app.include_router(
#     adac.router,
#     prefix="/adacs",
#     tags=["ADACS"],
# )

# app.include_router(
#     weidmuller.router,
#     prefix="/weidmuller",
#     tags=["Weidmuller"],
# )
