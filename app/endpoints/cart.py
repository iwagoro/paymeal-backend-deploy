from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import Users, Orders, OrderItems, Tickets
from .util.util import get_db, verify_token
from sqlalchemy import or_
import uuid

router = APIRouter()


#! カート内の商品を取得するエンドポイント (Array)
@router.get("/cart", status_code=200)
def get_carts(user=Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(Users).filter_by(email=user["email"]).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    cart = (
        db.query(Orders)
        .filter(Orders.user_id == user.id, or_(Orders.status == "not_purchased", Orders.status == "processing"))
        .first()
    )
    if not cart:
        return []

    tickets = db.query(OrderItems).filter_by(order_id=cart.id).all()
    result = {
        "id": cart.id,
        "status": cart.status,
        "items": [
            {"ticket": db.query(Tickets).filter_by(id=item.ticket_id).first(), "quantity": item.quantity}
            for item in tickets
        ],
    }
    return result


#! カートに商品を追加するエンドポイント
@router.post("/cart/{ticket_id}", status_code=201)
def add_ticket_to_cart(ticket_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(Users).filter_by(email=user["email"]).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    cart = db.query(Orders).filter_by(user_id=user.id, status="not_purchased").first()
    if not cart:
        cart = Orders(id=str(uuid.uuid4()), user_id=user.id, status="not_purchased")
        db.add(cart)
        db.commit()
        db.refresh(cart)

    cart_item = db.query(OrderItems).filter_by(order_id=cart.id, ticket_id=ticket_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = OrderItems(order_id=cart.id, ticket_id=ticket_id, quantity=1)
    db.add(cart_item)
    db.commit()
    return "Ticket added to cart"


#! カートから商品を減らすエンドポイント
@router.delete("/cart/{ticket_id}", status_code=201)
def remove_ticket_from_cart(ticket_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(Users).filter_by(email=user["email"]).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    cart = db.query(Orders).filter_by(user_id=user.id, status="not_purchased").first()
    if not cart:
        cart = Orders(id=str(uuid.uuid4()), user_id=user.id, status="not_purchased")
        db.add(cart)
        db.commit()
        db.refresh(cart)

    cart_item = db.query(OrderItems).filter_by(order_id=cart.id, ticket_id=ticket_id).first()
    if not cart_item:
        raise HTTPException(status_code=400, detail="Ticket not in cart")
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        db.commit()
        return "Ticket quantity reduced"
    else:
        db.delete(cart_item)
        db.commit()
        return "Ticket removed from cart"


#! カートから商品を削除するエンドポイント
@router.delete("/cart/{ticket_id}/all", status_code=201)
def delete_ticket_from_cart(ticket_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(Users).filter_by(email=user["email"]).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    cart = db.query(Orders).filter_by(user_id=user.id, status="not_purchased").first()
    if not cart:
        cart = Orders(id=str(uuid.uuid4()), user_id=user.id, status="not_purchased")
        db.add(cart)
        db.commit()
        db.refresh(cart)

    cart_item = db.query(OrderItems).filter_by(order_id=cart.id, ticket_id=ticket_id).first()
    if not cart_item:
        raise HTTPException(status_code=400, detail="Ticket not in cart")
    db.delete(cart_item)
    db.commit()
    return "Ticket removed from cart"
