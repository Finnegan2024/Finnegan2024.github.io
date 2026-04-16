# resources: https://fastapi.tiangolo.com/how-to/custom-request-and-route/?h=router#custom-apiroute-class-in-a-router
# https://fastapi.tiangolo.com/reference/templating/?h=jinja

# this file will return the admin dashboard page which leverages db queries to return
# the number of accounts, tasks, and devices within the project. This demonstrates my
# ability to enhance db functionality within a user-friendly environment.

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from auth import require_admin
from db import get_session
from models import Account, Device, Task

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin", response_class=HTMLResponse)
def get_admin_page(req: Request,
                   curr_admin: Account=Depends(require_admin),
                   session: Session=Depends(get_session)):
    account_count = len(session.exec(select(Account)).all())
    device_count = len(session.exec(select(Device)).all())
    task_count = len(session.exec(select(Task)).all())

    return templates.TemplateResponse(request=req,
                                      name="admin.html",
                                      context={
                                          "admin": curr_admin.role,
                                          "account_count": account_count,
                                          "device_count": device_count,
                                          "task_count": task_count
                                      })