# resources: https://fastapi.tiangolo.com/how-to/custom-request-and-route/?h=router#custom-apiroute-class-in-a-router
# https://fastapi.tiangolo.com/reference/templating/?h=jinja

# this file will return the account management page which leverages db queries to return
# a list of accounts within the project. This demonstrates my ability to enhance
# db functionality within a user-friendly environment

from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from auth import hash_password, require_admin
from db import get_session
from models import Account

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/accounts", response_class=HTMLResponse)
def get_accounts(
    req: Request,
    current_admin: Account=Depends(require_admin),
    session: Session=Depends(get_session)
):
    accounts = session.exec(select(Account)).all()

    return templates.TemplateResponse(
        request=req,
        name="accounts.html",
        context={
            "admin": current_admin,
            "accounts": accounts
        }
    )

@router.post("/accounts/create")
def create_accounts(
    account_name: Annotated[str, Form()],
    password: Annotated[str, Form()],
    role: Annotated[str, Form()],
    current_admin: Account=Depends(require_admin),
    session: Session=Depends(get_session)
):
    if current_admin:
        account = Account(
            account_name=account_name,
            hashed_password=hash_password(password),
            role=role
        )
        session.add(account)
        session.commit()

    return RedirectResponse(url="/accounts", status_code=303)

@router.post("/accounts/role/{account_id}")
def update_account_role(
    account_id: int,
    role: Annotated[str, Form()],
    current_admin: Account=Depends(require_admin),
    session: Session=Depends(get_session)
):
    if current_admin:
        account = session.get(Account, account_id)
        if account is not None:
            account.role = role
            session.add(account)
            session.commit()

    return RedirectResponse(url="/accounts", status_code=303)
