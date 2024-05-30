from fastapi import HTTPException, Depends, Response, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from models import Users, Orders, OrderItems, Tickets
from util.util import get_db, verify_token, create_response, create_error_response
from sqlalchemy.exc import SQLAlchemyError
import datetime

router = APIRouter()


# * 注文可能時間か確認する関数
def is_orderable_time():
    now = datetime.datetime.now()
    if now.hour > 11 or now.hour < 13:
        return True
    return False


# * ユーザを確認する関数
def get_user_by_email(db: Session, email: str):
    user = db.query(Users).filter_by(email=email).first()
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


#! 最新の注文を取得(status=purchased/ordered/completed)
@router.get("/orders/latest", status_code=200)
def get_latest_order(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])

    # ? 最新の注文を取得
    order = (
        db.query(Orders)
        .filter(
            Orders.user_id == target.id,
            or_(Orders.status == "purchased", Orders.status == "ordered", Orders.status == "completed"),
        )
        .order_by(desc(Orders.date))
        .first()
    )
    if not order:
        raise HTTPException(status_code=204, detail="No orders found")

    # ? レスポンスを作成
    tickets = db.query(OrderItems).filter_by(order_id=order.id).all()
    result = get_order_details(db, [order])
    return {"order": result[0]}


#! 全てのpurchased/ordered/completedを取得
@router.get("/orders/purchased", status_code=200)
def get_orders(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])

    # ? 注文を取得
    orders = (
        db.query(Orders)
        .filter(
            Orders.user_id == target.id,
            or_(Orders.status == "purchased", Orders.status == "ordered", Orders.status == "completed"),
        )
        .order_by(desc(Orders.date))
        .all()
    )
    if not orders:
        raise HTTPException(status_code=204, detail="No orders found")

    # ? レスポンスを作成
    result = get_order_details(db, orders)
    return {"orders": result}


#! 注文する
@router.post("/orders/{order_id}", status_code=201)
def create_order(order_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):

    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])
    # ? 注文を取得
    order = db.query(Orders).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "purchased":
        raise HTTPException(status_code=400, detail="Invalid order status")
    if not is_orderable_time():
        raise HTTPException(status_code=400, detail="Not orderable time")
    if order.date.date() != datetime.datetime.now().date():
        raise HTTPException(status_code=400, detail="Ticket is expired")

    try:
        # ?レスポンスを作成
        order.status = "ordered"
        db.add(order)
        db.commit()
        return Response(status_code=201)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Invalid Request")
