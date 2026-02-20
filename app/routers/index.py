from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import AuthDep
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status
from . import templates

index_router = APIRouter()

@index_router.get("/app", response_class=HTMLResponse)
async def index(
    request: Request,
    logged_in_user: AuthDep
):
    return templates.TemplateResponse(
        request=request, 
        name="todo.html",
        context={
            "current_user":logged_in_user
        }
    )
