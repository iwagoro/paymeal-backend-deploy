from fastapi import HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from models import Users, Orders, OrderItems, Tickets,Stocks
from paypay import create_payment, get_payment_details, delete_payment
from util.util import get_db, verify_token,get_user_by_email,get_today
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
        if ticket:
            stock = db.query(Stocks).filter_by(ticket_id=ticket.id).first()
            if stock:
                stock.unit_sales += item.quantity
                db.add(stock)

#! 決済リンクの取得
@router.get("/payment/", status_code=200)
def create_order(order_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    try:
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
        ticket_ids = [item.ticket_id for item in cart_items]
        tickets = db.query(Tickets, Stocks).join(Stocks, Stocks.ticket_id == Tickets.id).filter(Tickets.id.in_(ticket_ids)).all()

        ticket_stock_map = {ticket.Tickets.id: ticket for ticket in tickets}

        for item in cart_items:
            if item.ticket_id not in ticket_stock_map:
                raise HTTPException(status_code=400, detail=f"Ticket ID {item.ticket_id} not found")
            ticket, stock = ticket_stock_map[item.ticket_id]
            if stock.stock - stock.unit_sales < item.quantity:
                raise HTTPException(status_code=400, detail=f"Out of stock for Ticket ID {item.ticket_id}")

        # ? 注文の作成
        order_content = [
            {
                "name": ticket_stock_map[item.ticket_id].Tickets.name,
                "price": ticket_stock_map[item.ticket_id].Tickets.price,
                "quantity": item.quantity,
                "productId": str(item.ticket_id),
                "unitPrice": {"amount": ticket_stock_map[item.ticket_id].Tickets.price, "currency": "JPY"},
            }
            for item in cart_items
        ]

        # ? paypay決済リンクの作成
        total = sum(item.quantity * ticket_stock_map[item.ticket_id].Tickets.price for item in cart_items)
        url, code_id = create_payment(cart.id, order_content, total)

        # ? トランザクションの開始
        cart.status = "processing"
        cart.code_id = code_id
        cart.payment_link = url
        db.add(cart)
        
        # ? チケットの在庫を減らす
        decrease_ticket_quantity(cart_items, db)
        
        # ? コミット
        db.commit()
        
        return url

    # ? 重複エラー
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Order already exists")
    # ? その他のエラー
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid Request")

#! 決済を確認
@router.patch("/payment/", status_code=200)
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
    today = get_today()
    # ? 最後の注文番号を取得
    last_order = db.query(Orders).filter(Orders.purchase_date != None).order_by(Orders.purchase_date.desc()).first()

    # ? 今日初めての注文の場合
    if not last_order or (last_order != None and last_order.purchase_date != today):
        last_number = STARTING_ORDER_NUMBER
    # ? 今日の注文がある場合
    else:
        last_number = last_order.number + 1
    order_number = last_number

    try:
        # ? カートの更新
        cart.number = order_number
        cart.purchase_date = today
        cart.status = "purchased"
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return {"message": "Purchase completed"}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Invalid Request")


#! 決済リンクの削除
@router.delete("/payment/", status_code=200)
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
            ticket.stocks.unit_sales -= item.quantity
            db.add(ticket)
        db.commit()
        db.refresh(cart)
        return Response(status_code=201)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Invalid Request")

