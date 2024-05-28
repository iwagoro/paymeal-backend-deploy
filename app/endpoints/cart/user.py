from fastapi import HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from models import Users, Orders, OrderItems, Tickets
from util.util import get_db, verify_token, create_response, create_error_response
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
import uuid

router = APIRouter()


# * カート内の合計金額を計算
def calculate_total(db: Session, order_id: str) -> int:
    items = db.query(OrderItems).filter_by(order_id=order_id).all()
    total = sum([item.quantity * db.query(Tickets).filter_by(id=item.ticket_id).first().price for item in items])
    return total


# * ユーザーとカートの取得
def get_user_and_cart(db: Session, user_email: str):
    target = db.query(Users).filter_by(email=user_email).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    cart = (
        db.query(Orders)
        .filter(Orders.user_id == target.id, or_(Orders.status == "not_purchased", Orders.status == "processing"))
        .first()
    )
    if not cart:
        cart = Orders(id=str(uuid.uuid4()), user_id=target.id, status="not_purchased")
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return target, cart


#! カートを取得
@router.get("/cart", status_code=200)
def get_cart(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザとカートを取得
    target, cart = get_user_and_cart(db, user["email"])
    tickets = db.query(OrderItems).filter_by(order_id=cart.id).all()
    total = calculate_total(db, cart.id)
    # ? レスポンスの作成
    result = {
        "id": cart.id,
        "status": cart.status,
        "items": [
            {"ticket": db.query(Tickets).filter_by(id=item.ticket_id).first(), "quantity": item.quantity}
            for item in tickets
        ],
        "total": total,
    }
    return {"cart": result}


#! カートに商品を追加
@router.post("/cart/{ticket_id}")
def add_ticket_to_cart(ticket_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):

    # ? ユーザとカートを取得
    target, cart = get_user_and_cart(db, user["email"])
    cart_item = db.query(OrderItems).filter_by(order_id=cart.id, ticket_id=ticket_id).first()

    # ? カートに商品があるかどうかを確認
    try:
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = OrderItems(order_id=cart.id, ticket_id=ticket_id, quantity=1)
            db.add(cart_item)
        # ? カートの合計金額を計算
        cart.total = calculate_total(db, cart.id)
        db.commit()
        db.refresh(cart)
        return Response(status_code=200)

    # ? その他のエラー
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Invalid Request")


#! カートから商品を減らす
@router.delete("/cart/{ticket_id}")
def remove_ticket_from_cart(ticket_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):

    # ? ユーザとカートを取得
    target, cart = get_user_and_cart(db, user["email"])

    # ? カートに商品があるかどうかを確認
    cart_item = db.query(OrderItems).filter_by(order_id=cart.id, ticket_id=ticket_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    try:
        # ? カートから商品を減らす
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart.total = calculate_total(db, cart.id)
            db.commit()
            db.refresh(cart)
            return Response(status_code=201)
        # ? カートから商品を削除
        else:
            db.delete(cart_item)
            cart.total = calculate_total(db, cart.id)
            db.commit()
            db.refresh(cart)
            return Response(status_code=204)
    # ? その他のエラー
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Invalid Request")
