# controls the authentication functionality for this project by leveraging meaningful queries
# and keeping secure login functionality
# resource used: https://fastapi.tiangolo.com/tutorial/security/

from fastapi import Depends, HTTPException, Request, status
from pwdlib import PasswordHash
from sqlmodel import Session, select

from db import get_session
from models import Account

password_hash = PasswordHash.recommended()

def hash_password(password):
    return password_hash.hash(password)

# returns a boolean val
def verify_password(password, hashed_password):
    return password_hash.verify(password, hashed_password)

def authenticate_account(account_name, password, session):
    statement = select(Account).where(Account.account_name==account_name)
    account = session.exec(statement).first()

    if account is None:
        return None
    
    if not verify_password(password, account.hashed_password):
        return None
    
    return account

def get_current_account(req: Request, session: Session=Depends(get_session)):
    account_id = req.session.get("account_id")

    if account_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unvalid Credentials")
    
    account = session.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    return account

def require_admin(curr_account: Account = Depends(get_current_account)):
    if curr_account.role.lower() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access needed")
    
    return curr_account
