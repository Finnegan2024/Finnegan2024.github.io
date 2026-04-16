# resource: https://fastapi.tiangolo.com/how-to/custom-request-and-route/?h=router#custom-apiroute-class-in-a-router
# https://fastapi.tiangolo.com/reference/templating/?h=jinja

# this is a helper file to return db information

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from db import get_session
from models import Account, Reading, Device

router = APIRouter()

@router.get("/test-db")
def test_db(session: Session=Depends(get_session)):
    accounts = session.exec(select(Account)).all()
    readings = session.exec(select(Reading)).all()
    devices = session.exec(select(Device)).all()
    return {
        "account_count":len(accounts),
        "reading_count": len(readings),
        "device_count": len(devices)
    }