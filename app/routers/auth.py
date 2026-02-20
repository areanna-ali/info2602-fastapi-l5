from fastapi import APIRouter, HTTPException, Depends, Request, Response
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import encrypt_password, verify_password, create_access_token, AuthDep
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status
from . import templates
from fastapi.responses import HTMLResponse, RedirectResponse

auth_router = APIRouter(tags=["Authentication"])

@auth_router.post("/login")
async def login_action(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
    request: Request
) -> Response:
    # Try logging in a Regular User
    user = db.exec(select(RegularUser).where(RegularUser.username == form_data.username)).one_or_none()
    if not user or not verify_password(plaintext_password=form_data.password, encrypted_password=user.password):
        #Try logging in an admin
        user = db.exec(select(Admin).where(Admin.username == form_data.username)).one_or_none()
        if not user or not verify_password(plaintext_password=form_data.password, encrypted_password=user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    access_token = create_access_token(data={"sub": user.id, "role": user.role},)

    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header:
        # If web, we put token in the COOKIES
        max_age = 30 * 24 * 60 * 60
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, max_age=max_age, samesite="lax")

        return response
    return Token(access_token=access_token, token_type="bearer")


@auth_router.get("/identify", response_model=UserResponse)
def get_user_by_id(db: SessionDep, user:AuthDep):
    return user


@auth_router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup_user(user_data: UserCreate, db:SessionDep):
  try:
    new_user = RegularUser(
        username=user_data.username, 
        email=user_data.email, 
        password=encrypt_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    return new_user
  except Exception:
    db.rollback()
    raise HTTPException(
                status_code=400,
                detail="Username or email already exists",
                headers={"WWW-Authenticate": "Bearer"},
            )

@auth_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="login.html",
    )


@auth_router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="signup.html",
    )


# @auth_router.get("/logout",)
# async def logout(request: Request, response: Response):
#     accept_header = request.headers.get("accept", "")
#     accept_header = request.headers.get("accept", "")
#     if "text/html" in accept_header: # If web redirect to login
#         final_response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
#         final_response.delete_cookie(
#             key="access_token",
#             httponly=True,
#             samesite="lax"
#         )
#     else: # if mobile return response
#         final_response = JSONResponse(content={"detail": "Successfully logged out"})
    
#     return final_response