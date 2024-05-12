from fastapi import HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from ..database import Users
from .util.util import get_db, verify_token

router = APIRouter()


#! 全てのユーザを取得 (Array)
@router.get("/users", status_code=200)
async def get_users(db: Session = Depends(get_db)):
    users = db.query(Users).all()
    # ユーザーが存在しない場合は 204 エラーを返す
    if not users:
        return Response(status_code=204)

    return users


#! トークンからemailを取得 (string)
@router.get("/user", status_code=200)
async def get_user(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ユーザーを検索
    target_user = db.query(Users).filter_by(email=user["email"]).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    return target_user.email


#! トークンからユーザーを追加
@router.post("/user", status_code=201)
async def add_user(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ユーザーがすでに存在するかどうかを確認
    old_user = db.query(Users).filter_by(email=user["email"]).first()
    if old_user:
        raise HTTPException(status_code=409, detail="User already exists")

    new_user = Users(id=user["uid"], email=user["email"])
    db.add(new_user)
    db.commit()
    return "User added successfully"


#! ユーザを削除
@router.delete("/user", status_code=201)
async def delete_user(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ユーザーを検索
    target_user = db.query(Users).filter_by(email=user["email"]).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(target_user)
    db.commit()
    return "User deleted successfully"
