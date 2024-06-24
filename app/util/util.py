from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, Header
from requests import Session
from database import SessionLocal as SessionClass
from firebase_admin import auth
from dotenv import load_dotenv
load_dotenv()
from models import Users
import pytz


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
        

# * 今日の日付を取得
def get_today():
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    today = datetime.now(tokyo_tz).date()
    return today

# * 今月を取得
def get_this_month():
    today = get_today()
    month_start = today + relativedelta(day=1)
    month_end = today + relativedelta(months=+1,day=1,days=-1)
    return month_start,month_end

def get_last_month():
    today = get_today()
    month_start = today + relativedelta(day=1,months=-1)
    month_end = today + relativedelta(day=1,days=-1)
    return month_start,month_end



# * 機能の日付を取得
def get_yesterday():
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    today = datetime.now(tokyo_tz).date()
    return today - timedelta(days=1)


# * 注文可能時間か確認する関数
def is_orderable_time():
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    now = datetime.now(tokyo_tz)
    if now.hour >= 11 and now.hour <= 13:
        return True
    return False


# * ユーザーの認証を行うエンドポイント
def verify_token(authorization: str = Header(None)):
    token = authorization.split(" ")[1] if authorization else None
    if not token:
        raise HTTPException(status_code=401, detail="Need Token")
    try:
        decoded_token = auth.verify_id_token(token)
        return {"uid": decoded_token["uid"], "email": decoded_token["email"]}
    except Exception as e:
        print(token)
        print(e)
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")


# * ユーザを確認する関数
def get_user_by_email(db: Session, email: str):
    user = db.query(Users).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    return user