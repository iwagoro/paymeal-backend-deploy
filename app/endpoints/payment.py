from fastapi import HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from models import Users, Orders, OrderItems, Tickets
from paypay import create_payment, get_payment_details, delete_payment
from util.util import get_db, verify_token
from datetime import datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import pytz

router = APIRouter()

# 初期注文番号
STARTING_ORDER_NUMBER = 200


# * チケットを減らす関数
def decrease_ticket_quantity(tickets, db: Session):
    for item in tickets:
        ticket = db.query(Tickets).filter_by(id=item.ticket_id).first()
        ticket.stock -= item.quantity
        db.add(ticket)


# * ユーザを確認する関数
def get_user_by_email(db: Session, email: str):
    user = db.query(Users).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


#! 決済リンクの取得
@router.post("/payment/create/{order_id}", status_code=200)
def create_order(order_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザの確認
    target = get_user_by_email(db, user["email"])

    # ? カートの確認
    cart = db.query(Orders).filter_by(user_id=target.id, id=order_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    # ? カートが購入済みでないことを確認
    if cart.status != "not_purchased":
        raise HTTPException(status_code=400, detail="Invalid Request")

    # ? カートにアイテムがあることを確認
    cart_items = db.query(OrderItems).filter_by(order_id=cart.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # ? カート内の各アイテムの在庫があるか確認
    for item in cart_items:
        ticket = db.query(Tickets).filter_by(id=item.ticket_id).first()
        if ticket.stock < item.quantity:
            raise HTTPException(status_code=400, detail="Out of stock")

    # ? 注文の作成
    order_content = []
    for item in cart_items:
        ticket = db.query(Tickets).filter_by(id=item.ticket_id).first()
        order_content.append(
            {
                "name": ticket.name,
                "price": ticket.price,
                "quantity": item.quantity,
                "productId": str(ticket.id),
                "unitPrice": {"amount": ticket.price, "currency": "JPY"},
            }
        )
    # ? paypay決済リンクの作成
    total = sum([item.quantity * db.query(Tickets).filter_by(id=item.ticket_id).first().price for item in cart_items])
    url, code_id = create_payment(cart.id, order_content, total)

    try:
        # ? カートの更新
        cart.status = "processing"
        cart.code_id = code_id
        cart.payment_link = url
        db.add(cart)
        # ? チケットの在庫を減らす
        decrease_ticket_quantity(cart_items, db)
        db.commit()
        return {"url": url, "code_id": code_id}
    # ? 重複エラー
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Order already exists")
    # ? その他のエラー
    except SQLAlchemyError:
        raise HTTPException(status_code=400, detail="Invalid Request")


#! 決済を確認
@router.post("/payment/confirm/{order_id}", status_code=200)
def complete_purchase(order_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザの確認
    target = get_user_by_email(db, user["email"])

    # ? カートの確認
    cart = db.query(Orders).filter_by(user_id=target.id, id=order_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    # ? カートが購入済みか確認
    state = get_payment_details(cart.id)

    # ? 注文情報の更新
    last_number = 0
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    today = datetime.now(tokyo_tz)
    # ? 最後の注文番号を取得
    last_order = db.query(Orders).filter(Orders.date != None).order_by(Orders.date.desc()).first()

    # ? 今日初めての注文の場合
    if not last_order or (last_order != None and last_order.date.date() != today):
        last_number = STARTING_ORDER_NUMBER
    # ? 今日の注文がある場合
    else:
        last_number = last_order.number + 1
    order_number = last_number

    try:
        # ? カートの更新
        cart.number = order_number
        cart.date = today
        cart.status = "purchased"
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return Response(status_code=201)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Invalid Request")


#! 決済リンクの削除
@router.delete("/payment/delete/{order_id}", status_code=200)
def delete_payment_endpoint(order_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザの確認
    target = get_user_by_email(db, user["email"])
    # ? カートの確認
    cart = db.query(Orders).filter_by(user_id=target.id, id=order_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="CART NOT FOUND")
    # ? 決済の削除
    state = delete_payment(cart.code_id)

    try:
        # ? カートの更新
        cart.payment_link = None
        cart.code_id = None
        cart.status = "not_purchased"
        # ? チケットの在庫を戻す
        cart_items = db.query(OrderItems).filter_by(order_id=cart.id).all()
        for item in cart_items:
            ticket = db.query(Tickets).filter_by(id=item.ticket_id).first()
            ticket.stock += item.quantity
            db.add(ticket)
        db.commit()
        db.refresh(cart)
        return Response(status_code=201)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Invalid Request")


#! 決済をキャンセル
@router.delete("/payment/cancel/{order_id}", status_code=200)
def cancel_payment(order_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザの確認
    target = get_user_by_email(db, user["email"])
    # ? カートの確認
    cart = db.query(Orders).filter_by(user_id=target.id, id=order_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="CART NOT FOUND")

    # ?決済のキャンセル
    state = delete_payment(cart.code_id)

    try:
        # ? カートの更新
        cart.payment_link = None
        cart.code_id = None
        cart.status = "not_purchased"
        db.add(cart)
        # ? チケットの在庫を戻す
        cart_items = db.query(OrderItems).filter_by(order_id=cart.id).all()
        for item in cart_items:
            ticket = db.query(Tickets).filter_by(id=item.ticket_id).first()
            ticket.stock += item.quantity
            db.add(ticket)
        db.commit()
        return Response(status_code=201)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Invalid Request")
