from fastapi import HTTPException, Header
from ...database import SessionClass
from firebase_admin import auth


# * データベースセッションを作成する依存関係
def get_db():
    db = SessionClass()
    try:
        yield db
    finally:
        db.close()


# * ユーザーの認証を行うエンドポイント
def verify_token(authorization: str = Header(None)):
    token = authorization.split(" ")[1] if authorization else None
    if not token:
        raise HTTPException(status_code=401, detail="Authorization token missing")
    try:
        decoded_token = auth.verify_id_token(token)
        return {"uid": decoded_token["uid"], "email": decoded_token["email"]}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
