# resource: https://fastapi.tiangolo.com/how-to/custom-request-and-route/?h=router#custom-apiroute-class-in-a-router
# https://fastapi.tiangolo.com/reference/templating/?h=jinja

# this file will return the latest reading record used by the user dashboard to present
# the entire record. This demonstrates my ability to enhance db functionality within a 
# user-friendly environment by leveraging meaningful queries and taking advantage of
# schema design.

from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from auth import get_current_account
from db import get_session
from models import Account, Device, Reading

router = APIRouter()

@router.get("/latest-reading")
def get_latest_reading(device_name: Annotated[str, Query()],
                       current_account: Account=Depends(get_current_account),
                       session: Session=Depends(get_session)):
    device_statement = select(Device).where(Device.device_name == device_name)
    device = session.exec(device_statement).first()

    if device is None:
        return {
            "success": False,
            "reason": "Device not found"
        }
    
    is_admin = current_account.role.lower() == "admin"
    owns_device = device.owner_id == current_account.account_id

    if not is_admin and not owns_device:
        return {
            "success": False,
            "reason": "Not authorized"
        }
    
    reading_statement = select(Reading).where(Reading.linked_device_id == device.device_name).order_by(Reading.timestamp.desc())
    latest_reading = session.exec(reading_statement).first()

    if latest_reading is None:
        return {
            "success": True,
            "device_name": device_name,
            "message": "No readings found",
            "reading": None
        }
    
    return {
        "success": True,
        "device_name": device_name,
        "reading": {
            "reading_id": latest_reading.reading_id,
            "state": latest_reading.state,
            "set_point": latest_reading.set_point,
            "current_temp": latest_reading.current_temp,
            "timestamp": latest_reading.timestamp,
            "nonce": latest_reading.nonce
        }
    }
