from fastapi import  HTTPException, Depends
from sqlalchemy.orm import Session
from ..schema import  UserEmail , UserId
from ..database import  Users
from fastapi import APIRouter
from ..database import SessionClass
import uuid

router = APIRouter()

# データベースセッションを作成する依存関係
def get_db():
    db = SessionClass()
    try:
        yield db
    finally:
        db.close()


#全てのユーザーを取得するエンドポイント
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(Users).all()


#新しいユーザーを作成するエンドポイント
@router.post("/users", response_model=str)
def create_user(user_email: UserEmail, db: Session = Depends(get_db)):
    # 既存のユーザーを検索
    existing_user = db.query(Users).filter_by(email=user_email.email).first()
    if existing_user:
        # ユーザーがすでに存在する場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User already exists with this email")

    # 新しいユーザーを追加
    user_id = str(uuid.uuid4())
    new_user = Users(id=user_id, email=user_email.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return "User created"


#既存ユーザを削除するエンドポイント
@router.delete("/users", response_model=str)
def delete_user(user_id: UserId, db: Session = Depends(get_db)):
    # ユーザーが存在するか確認
    user = db.query(Users).filter_by(id=user_id.id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User does not exist with this id")

    # ユーザーを削除
    db.delete(user)
    db.commit()
    return "User deleted"