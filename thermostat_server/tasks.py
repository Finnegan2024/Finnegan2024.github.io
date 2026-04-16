# resource: https://fastapi.tiangolo.com/how-to/custom-request-and-route/?h=router#custom-apiroute-class-in-a-router
# https://fastapi.tiangolo.com/reference/templating/?h=jinja

# this file will return the task management page which leverages db queries to return
# the number of tasks and allows developers and admins to resolve tasks. This 
# demonstrates my ability to enhance db functionality within a user-friendly environment
# by creating a collaborative environment to support decision making

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from auth import require_admin
from db import get_session
from models import Account, Task

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/tasks", response_class=HTMLResponse)
def get_tasks_page(
    req: Request,
    current_admin: Account=Depends(require_admin),
    session: Session=Depends(get_session)
):
    tasks = session.exec(select(Task)).all()

    return templates.TemplateResponse(
        request=req,
        name="tasks.html",
        context={
            "admin": current_admin,
            "tasks": tasks,
        }
    )

@router.post("/tasks/create")
def create_task(
    task_name: Annotated[str, Form()],
    task_issue: Annotated[str, Form()],
    current_admin: Account=Depends(require_admin),
    session: Session=Depends(get_session)
):
    task = Task(
        task_name=task_name,
        task_issue=task_issue,
        created_by=str(current_admin.account_name),
        created_on=datetime.now().isoformat()
    )
    session.add(task)
    session.commit()

    return RedirectResponse(url="/tasks", status_code=303)

@router.post("/tasks/resolve/{task_id}")
def resolve_task(
    task_id: int,
    current_admin: Account=Depends(require_admin),
    session: Session=Depends(get_session)
):
    task = session.get(Task, task_id)
    if task is not None:
        task.resolved_by = current_admin.account_id
        task.resolved_on = datetime.now().isoformat()
        session.add(task)
        session.commit()

    return RedirectResponse(url="/tasks", status_code=303)