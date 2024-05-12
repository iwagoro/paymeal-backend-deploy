from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import Users, Orders, OrderItems, Tickets
from ..paypay import create_payment, get_payment_details
from .util.util import get_db, verify_token

router = APIRouter()


# * チケットを減らす関数
def decrease_ticket_quantity(tickets, db: Session):
    for item in tickets:
        ticket = db.query(Tickets).filter_by(id=item.ticket_id).first()
        ticket.stock -= item.quantity
        db.add(ticket)


#! カート内の商品を購入するためのQRコードを作成するエンドポイント、statusはprocessingに変更
@router.get("/payment/{order_id}", status_code=200)
def create_order(order_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    # ユーザーを検索
    user = db.query(Users).filter_by(email=user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    #  カートを検索
    cart = db.query(Orders).filter_by(user_id=user.id, id=order_id).first()
    if not cart:
        # カートが存在しない場合は 404 エラーを返す
        raise HTTPException(status_code=404, detail="Cart is not exist")

    if cart.status != "not_purchased":
        raise HTTPException(status_code=400, detail="Cart is already purchased")

    cart_items = db.query(OrderItems).filter_by(order_id=cart.id).all()
    if not cart_items:
        # カートが存在しない場合は 404 エラーを返す
        raise HTTPException(status_code=404, detail="Cart is empty")

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

    total = sum([item.quantity * db.query(Tickets).filter_by(id=item.ticket_id).first().price for item in cart_items])
    url, code_id = create_payment(cart.id, order_content, total)

    cart.status = "processing"
    cart.code_id = code_id
    cart.payment_link = url
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return url


#! 決済が完了したか確認するエンドポイント
@router.post("/payment/{order_id}", status_code=200)
def complete_purchase(order_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(Users).filter_by(email=user["email"]).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # カートを検索
    cart = db.query(Orders).filter_by(user_id=user.id, id=order_id).first()
    if not cart:
        # カートが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=404, detail="Cart is not found")

    state = get_payment_details(cart.id)

    if state == "SUCCESS":
        # チケットの在庫を減らす
        tickets = db.query(OrderItems).filter_by(order_id=cart.id).all()
        decrease_ticket_quantity(tickets, db)
        cart.status = "purchased"
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return "Purchase completed"

    else:
        raise HTTPException(status_code=400, detail="Payment not completed")
