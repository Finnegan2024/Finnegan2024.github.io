# resource: https://fastapi.tiangolo.com/how-to/custom-request-and-route/?h=router#custom-apiroute-class-in-a-router
# https://fastapi.tiangolo.com/reference/templating/?h=jinja

# this file will return the login page which authenticates the user and returns the proper
# dashboard depending on the account type. This demonstrates my ability to enhance 
# db functionality within a user-friendly environment by improving upon security using 
# login credentials.

from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from auth import authenticate_account
from db import get_session

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
def root():
    return RedirectResponse(url="/login", status_code=303)

@router.get("/login", response_class=HTMLResponse)
def get_login_page(req: Request):
    return templates.TemplateResponse(request=req, name="login.html", context={"message":""})

@router.post("/login", response_class=HTMLResponse)
def post_login_page(req: Request,
                    account_name: Annotated[str, Form()],
                    password: Annotated[str, Form()],
                    session: Session=Depends(get_session)):
    account = authenticate_account(account_name, password, session)

    # redirect invalid attempt back to login page
    if account is None:
        return templates.TemplateResponse(request=req, name="login.html", context={"message":"Invalid login"})
    
    req.session["account_id"] = account.account_id
    req.session["role"] = account.role

    if account.role.lower() == "admin":
        return RedirectResponse(url="/admin", status_code=303)
    
    return RedirectResponse(url="/dashboard", status_code=303)
