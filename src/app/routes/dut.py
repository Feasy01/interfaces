from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/configuration")
def get_current_dut_configuration(Request: Request) -> {}:
    manager = Request.app.state.manager
    # print(manager.dut)
    return manager.dut


@router.post("/configuration")
async def set_current_dut_configuration(Request: Request) -> {}:
    new_config = await Request.json()
    manager = Request.app.state.manager
    manager.dut.clear()
    manager.set_config(new_config)
    return manager.dut
