from fastapi import HTTPException, Depends, Response, APIRouter, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from models import Users, Orders, OrderItems, Tickets, AdminUsers
from util.util import get_db, verify_token, create_error_response, create_response
from datetime import datetime
from typing import Optional
import pytz

router = APIRouter()


# * ユーザを確認する関数
def get_user_by_email(db: Session, email: str):
    user = db.query(AdminUsers).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# * 注文とチケットを取得する関数
def get_order_details(db: Session, orders):
    result = []
    for order in orders:
        # ? OrderItemsを取得
        order_items = db.query(OrderItems).filter_by(order_id=order.id).all()
        obj = {
            "id": order.id,
            "status": order.status,
            # ? OrderItemsからTicketを取得
            "items": [
                {"ticket": db.query(Tickets).filter_by(id=item.ticket_id).first(), "quantity": item.quantity}
                for item in order_items
            ],
            "number": order.number if hasattr(order, "number") else None,
            "date": order.date if hasattr(order, "date") else None,
            "total": order.total if hasattr(order, "total") else None,
        }
        result.append(obj)
    return result


#! 今日の注文を取得する
@router.get("/orders/today")
def get_today_orders(user=Depends(verify_token), db: Session = Depends(get_db)):

    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])

    # ? 今日の注文を取得
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    today = datetime.now(tokyo_tz).date()
    orders = (
        db.query(Orders)
        .filter(
            or_(Orders.status == "purchased", Orders.status == "ordered", Orders.status == "completed"),
            Orders.date == today,
        )
        .all()
    )
    if not orders:
        raise HTTPException(status_code=204, detail="No orders found")

    # ? レスポンスを作成
    result = get_order_details(db, orders)
    return {"orders": result}


#! 注文を完了にするエンドポイント
@router.post("/orders/complete/{order_id}", status_code=201)
def complete_order(order_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):

    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])
    # ? 注文を取得
    order = db.query(Orders).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "ordered":
        raise HTTPException(status_code=400, detail="Order is not in ordered state")

    try:
        order.status = "completed"
        db.add(order)
        db.commit()
        return Response(status_code=201)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Invalid Request")
