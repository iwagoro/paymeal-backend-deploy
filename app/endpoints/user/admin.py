from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import or_
from util.util import get_db, verify_token, create_error_response, create_response
from models import Users, AdminUsers, Orders
from schema import AdminSchema
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from fastapi import Response
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import os


router = APIRouter()


# * ユーザを確認する関数
def get_user_by_email(db: Session, email: str):
    user = db.query(AdminUsers).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    return user


#! email/idを取得 (string)
@router.get("/admin")
async def get_admin_user(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])
    # ? レスポンスの作成
    return {"user": target}


#! 追加
@router.post("/admin")
async def add_admin_user(user_info: AdminSchema, user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? secret keyの確認
    if user_info.password != os.environ.get("ADMIN_PASSWORD"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # ? Usersテーブルにユーザが存在するか確認
        target_user = db.query(Users).filter_by(email=user["email"]).first()
        if not target_user:
            new_user = Users(email=user["email"], id=user["uid"])
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

        # ? 新しい管理者を追加
        new_admin_user = AdminUsers(id=user["uid"], email=user["email"])
        db.add(new_admin_user)
        db.commit()
        db.refresh(new_admin_user)
        return Response(status_code=201)

    # ? 競合エラー
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    # ? その他のエラー
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


#! 削除
@router.delete("/admin", status_code=201)
async def delete_admin_user(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザの取得
    target = get_user_by_email(db, user["email"])

    try:
        # ? ユーザーを削除
        db.delete(target)
        db.commit()
        return Response(status_code=204)
    except SQLAlchemyError:
        raise HTTPException(status_code=400, detail="Invalid request")
