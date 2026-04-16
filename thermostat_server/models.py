# this is the models file to define the tables in our db. This file demonstrates my ability
# to implement device identification and authentication with meaningful schema designs
# resource used: https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-app-with-a-single-model

from sqlmodel import SQLModel, Field


class Account(SQLModel, table=True):
    account_id: int | None = Field(default=None, primary_key=True)
    account_name: str = Field(index=True, unique=True)
    hashed_password: str
    role: str = Field(index = True)


class Device(SQLModel, table=True):
    device_id: int | None = Field(default=None, primary_key=True)
    device_name: str = Field(index=True, unique=True)
    owner_id: int = Field(foreign_key="account.account_id")


class Reading(SQLModel, table=True):
    reading_id: int | None = Field(default=None, primary_key=True)
    nonce: int = Field(index=True)
    state: str
    set_point: int
    current_temp: int
    timestamp: float
    linked_device_id: str = Field(foreign_key="device.device_name")


class Task(SQLModel, table=True):
    task_id: int | None = Field(default=None, primary_key=True)
    task_name: str
    task_issue: str
    created_by: str
    created_on: str
    resolved_by: str | None = None
    resolved_on: str | None = None
