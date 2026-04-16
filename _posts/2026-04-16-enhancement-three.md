---
layout: post
title: "Enhancement #3: FastAPI Thermostat Server with Secure Database Integration"
date: 2026-04-16
categories: [DATABASES, FASTAPI, SECURITY]
---

**Repository:** [Thermostat Server](https://github.com/Finnegan2024/Finnegan2024.github.io/tree/main/thermostat_server)

## Overview

This enhancement builds the server-side component of the thermostat pipeline introduced in Enhancement #1. Where Enhancement #1 focused on the device's data transport layer, this enhancement focuses on what happens when that data arrives by validating it, storing it, and exposing it through a structured API built with **FastAPI** and **SQLModel** backed by a **SQLite** database.

The server receives temperature readings from a Raspberry Pi device, authenticates them via HMAC signature and nonce-based replay protection, persists them to a relational database, and serves that data through role-separated routes for users and administrators.

## Design Decisions and Trade-offs

**Role-based access control (RBAC).** Accounts are assigned either a `user` or `admin` role at creation. Route dependencies (`require_admin`, `get_current_account`) enforce this at the handler level, keeping authorization logic centralized in `auth.py` rather than scattered across routes.

**Nonce-based replay protection in `validators.py`.** Each ingested packet includes a nonce that is checked against previously seen values in the database. A replayed packet — one with a valid signature but a reused nonce — is rejected before a `Reading` record is ever written. This prevents an attacker who intercepts a valid transmission from resubmitting it.

**Secret key via environment variable.** The HMAC secret shared between the device and server is loaded through `pydantic-settings` at startup rather than hardcoded:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
```

If `SECRET_KEY` is absent from the environment, the application raises a validation error at startup . A deliberate fail-fast design that prevents the server from running in an insecure state.

**SQLModel over raw SQL.** SQLModel combines SQLAlchemy and Pydantic, allowing models to serve as both ORM definitions and validation schemas. This reduces the surface area for injection vulnerabilities since queries are constructed through the ORM rather than string formatting.

## Route Structure

| Module | Role Required | Purpose |
|---|---|---|
| `login.py` | None | Session-based authentication |
| `dashboard.py` | User | View owned devices and latest reading |
| `admin.py` | Admin | Overview of accounts, devices, tasks |
| `accounts.py` | Admin | Create accounts, manage roles |
| `devices.py` | Admin | Create and delete devices |
| `tasks.py` | Admin | Create and resolve support tasks |
| `ingestion.py` | Device (HMAC) | Receive and store temperature readings |
| `latest_reading.py` | User/Admin | Fetch latest reading for a device |

The `ingestion` route is the bridge between Enhancement #1 and this enhancement. It accepts the raw packet from the Pi, delegates to `validators.py` for authentication, then writes the result to the `Reading` table.

## Database Schema

Three core tables support the application:

- **Account** — stores credentials (bcrypt-hashed passwords), role, and session identity
- **Device** — links a named device to an owner account
- **Reading** — stores each ingested packet: temperature, state, set point, nonce, and timestamp, foreign-keyed to a device name

The schema is intentionally normalized so that querying the latest reading for a device is a single filtered and ordered select.

## Reflection

The primary challenge was designing the boundary between the device-facing ingestion endpoint and the user-facing dashboard routes. Both touch the same `Reading` table but have entirely different trust models — one authenticates via HMAC, the other via session cookie. Keeping these concerns separate while sharing the same database session dependency required deliberate layering in `auth.py` and `validators.py`.

Integrating environment-based secret management also reinforced that security decisions made at the infrastructure level (where the key lives) directly constrain what is safe to do at the application level (how the key is used). The two enhancements together form a closed loop: the device signs, the server verifies, and neither side exposes the shared secret.
