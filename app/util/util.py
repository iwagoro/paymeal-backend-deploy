from fastapi import HTTPException, Header
from database import SessionLocal as SessionClass
from firebase_admin import auth
from fastapi.responses import JSONResponse

from fastapi.encoders import jsonable_encoder
from schema import ErrorResponseModel, ResponseModel
from typing import Any


# * データベースセッションを作成する依存関係
def get_db():
    db = SessionClass()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# * ユーザーの認証を行うエンドポイント
def verify_token(authorization: str = Header(None)):
    token = authorization.split(" ")[1] if authorization else None
    if not token:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    try:
        decoded_token = auth.verify_id_token(token)
        return {"uid": decoded_token["uid"], "email": decoded_token["email"]}
    except Exception as e:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")


# * レスポンスを作成する関数
def create_response(status: str, code: int, message: str, data: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=code, content=ResponseModel(code=code, message=message, data=jsonable_encoder(data)).model_dump()
    )


# * エラーレスポンスを作成する関数
def create_error_response(code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=code, content=ErrorResponseModel(code=code, message=message).model_dump())
