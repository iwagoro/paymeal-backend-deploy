from fastapi import HTTPException, Depends, Response
from sqlalchemy.orm import Session
from ..database import Users, Orders, OrderItems, Tickets
from fastapi import APIRouter
from .util.util import get_db, verify_token
from sqlalchemy import or_
import datetime

router = APIRouter()


# * 注文可能時間か確認する関数
def is_orderable_time():
    now = datetime.datetime.now()
    if now.hour > 11 or now.hour < 18:
        return True
    return False


#! 過去の購入履歴を取得するエンドポイント (Array{orders,items})
@router.get("/orders", status_code=200)
def get_orders(user=Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(Users).filter_by(email=user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ユーザーの過去の注文を取得
    orders = db.query(Orders).filter_by(user_id=user.id).all()
    if not orders:
        # 注文が存在しない場合は 204 エラーを返す
        return Response(status_code=204)

    # 注文のアイテムを取得
    order_items = []
    for order in orders:
        items = db.query(OrderItems).filter_by(order_id=order.id).all()
        order_items.append({"order": order, "items": items})
    return order_items


#! 注文可能オーダを取得するエンドポイント
@router.get("/order", status_code=200)
def get_order(user=Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(Users).filter_by(email=user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 注文可能なカートを取得
    order = (
        db.query(Orders)
        .filter(Orders.user_id == user.id, or_(Orders.status == "purchased", Orders.status == "ordered"))
        .first()
    )
    if not order:
        return Response(status_code=204)

    tickets = db.query(OrderItems).filter_by(order_id=order.id).all()
    result = {
        "id": order.id,
        "status": order.status,
        "date": order.date,
        "items": [
            {"ticket": db.query(Tickets).filter_by(id=item.ticket_id).first(), "quantity": item.quantity}
            for item in tickets
        ],
    }
    return result


#! 注文を作成するエンドポイント
@router.post("/order/{order_id}", status_code=200)
def create_order(order_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    # ユーザーを検索
    user = db.query(Users).filter_by(email=user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 注文を検索
    order = db.query(Orders).filter_by(user_id=user.id, id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 注文が購入されていない場合はエラーを返す
    if order.status != "purchased":
        if order.status == "ordered":
            raise HTTPException(status_code=400, detail="Order is already created")

        elif order.status == "completed":
            raise HTTPException(status_code=400, detail="Order is already completed")

        else:
            raise HTTPException(status_code=400, detail="Order is not purchased")

    # 注文可能時間か確認
    if not is_orderable_time():
        raise HTTPException(status_code=400, detail="Order is not available at this time")

    order.status = "ordered"
    db.add(order)
    db.commit()
    return "Order created"
