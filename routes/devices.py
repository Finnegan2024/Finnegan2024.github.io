# resource: https://fastapi.tiangolo.com/how-to/custom-request-and-route/?h=router#custom-apiroute-class-in-a-router
# https://fastapi.tiangolo.com/reference/templating/?h=jinja

# this file will return the device management page which leverages db queries to return
# a list of accounts and devices within the project. This demonstrates my
# ability to enhance db functionality within a user-friendly environment.

from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from auth import require_admin
from db import get_session
from models import Account, Device

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/devices", response_class=HTMLResponse)
def get_devices_page(
    req: Request,
    current_admin: Account=Depends(require_admin),
    session: Session=Depends(get_session)
):
    devices = session.exec(select(Device)).all()
    accounts = session.exec(select(Account)).all()

    return templates.TemplateResponse(
        request=req,
        name="devices.html",
        context={
            "admin": current_admin,
            "devices": devices,
            "accounts": accounts
        }
    )

@router.post("/devices/create")
def create_device(
    name: Annotated[str, Form()],
    owner_id: Annotated[int, Form()],
    current_admin: Account=Depends(require_admin),
    session: Session=Depends(get_session)
):
    if current_admin:
        device = Device(
            device_name=name,
            owner_id=owner_id
        )
        session.add(device)
        session.commit()

    return RedirectResponse(url="/devices", status_code=303)

@router.post("/devices/delete/{device_id}")
def delete_device(
    device_id: int,
    current_admin: Account=Depends(require_admin),
    session: Session=Depends(get_session)
):
    if current_admin:
        device = session.get(Device, device_id)

        if device is not None:
            session.delete(device)
            session.commit()

    return RedirectResponse(url="/devices", status_code=303)
