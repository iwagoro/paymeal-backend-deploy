from fastapi import  HTTPException, Depends
from sqlalchemy.orm import Session
from ..schema import  User
from ..database import  Users
from fastapi import APIRouter
from ..database import SessionClass

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
def create_user(user: User, db: Session = Depends(get_db)):
    # 既存のユーザーを検索
    existing_user = db.query(Users).filter_by(email=user.email).first()
    if existing_user:
        # ユーザーがすでに存在する場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User already exists with this email")

    # 新しいユーザーを追加
    new_user = Users(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return "User created"


#既存ユーザを削除するエンドポイント
@router.delete("/users/{user_id}", response_model=str)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # ユーザーが存在するか確認
    user = db.query(Users).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User does not exist with this id")

    # ユーザーを削除
    db.delete(user)
    db.commit()
    return "User deleted"