# resources: https://fastapi.tiangolo.com/how-to/custom-request-and-route/?h=router#custom-apiroute-class-in-a-router
# https://fastapi.tiangolo.com/reference/templating/?h=jinja

# this file will return the user dashboard page which leverages db queries to return
# the list of devices belonging to the user and the device's latest reading. This 
# demonstrates my ability to enhance db functionality within a user-friendly environment.


from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from auth import get_current_account
from db import get_session
from models import Account, Device, Reading

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(req: Request,
                  curr_account: Account=Depends(get_current_account),
                  session: Session=Depends(get_session)):
    if curr_account.role.lower() == "admin":
        return RedirectResponse(url="/admin", status_code=303)
    
    device_statement = select(Device).where(Device.owner_id == curr_account.account_id)
    devices = session.exec(device_statement).all()

    selected_device = devices[0] if devices else None
    latest_reading = None

    if selected_device is not None:
        reading_statement = select(Reading).where(Reading.linked_device_id == selected_device.device_name).order_by(Reading.timestamp.desc())
        latest_reading = session.exec(reading_statement).first()
    
    return templates.TemplateResponse(
        request=req,
        name="dashboard.html",
        context={
            "account": curr_account,
            "devices": devices,
            "selected_device": selected_device,
            "latest_reading": latest_reading
        }
    )