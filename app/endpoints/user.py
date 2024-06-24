from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func, or_,and_
from util.util import get_db, verify_token, get_user_by_email,get_this_month,get_today,get_last_month
from models import Users, Orders
from fastapi.responses import  Response
from sqlalchemy.sql import extract
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

router = APIRouter()


#! email/idを取得
@router.get("/user")
async def get_user(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])
    # ? レスポンスの作成
    return target


#! 追加
@router.post("/user")
async def add_user(user=Depends(verify_token), db: Session = Depends(get_db)):
    try:
        # ? レスポンスの作成
        new_user = Users(id=user["uid"], email=user["email"])
        db.add(new_user)
        db.commit()
        return Response(status_code=201)
    # ? 競合エラー
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    # ? その他のエラー
    except SQLAlchemyError:
        raise HTTPException(status_code=400, detail="Invalid Request")
    
@router.post("/user/notification")
async def add_notification_token(token: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    try:
        # ? ユーザを取得
        target = get_user_by_email(db, user["email"])
        # ? 通知トークンを更新
        target.notification_token = token
        db.commit()
        return {"message": "Notification token added successfully"}
    # ? その他のエラー
    except SQLAlchemyError:
        raise HTTPException(status_code=400, detail="Invalid Request")
    
@router.delete("/user/notification")    
async def delete_notification_token(user=Depends(verify_token), db: Session = Depends(get_db)):
    try:
        # ? ユーザを取得
        target = get_user_by_email(db, user["email"])
        # ? 通知トークンを削除
        target.notification_token = None
        db.commit()
        return {"message": "Notification token deleted successfully"}
    # ? その他のエラー
    except SQLAlchemyError:
        raise HTTPException(status_code=400, detail="Invalid Request")


#! ユーザの今月と先月の購入額を取得
@router.get("/user/usage", status_code=200)
async def get_user_monthly_usage(user=Depends(verify_token), db: Session = Depends(get_db)):
    
    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])
    today = get_today()
    month_start,month_end = get_this_month()
    last_month_start,last_month_end = get_last_month()
    
    # ? 今月の購入額を集計
    current_month_total = db.query(func.sum(Orders.total).filter(Orders.user_id==target.id,and_(
        Orders.purchase_date >= month_start,
        Orders.purchase_date <= month_end
    
    ))).scalar()
    
    # ? 先月の購入額を集計
    last_month_total = db.query(func.sum(Orders.total).filter(Orders.user_id==target.id,and_(
        Orders.purchase_date >= last_month_start,
        Orders.purchase_date <= last_month_end
    
    ))).scalar()
    
    # ? 結果を返す
    return {
        "current_month_total": current_month_total or 0,
        "last_month_total": last_month_total or 0
    }

