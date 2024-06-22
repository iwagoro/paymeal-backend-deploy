from fastapi import HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from models import Users, Orders, OrderItems, Tickets
from util.util import get_db, verify_token, get_user_by_email
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
import uuid

router = APIRouter()


#! カートを取得
@router.get("/cart", status_code=200)
def get_cart(user=Depends(verify_token), db: Session = Depends(get_db)):
    #? ユーザの取得
    target = get_user_by_email(db, user["email"])
    
    #? カートの取得
    cart = db.query(Orders).filter(Orders.user_id==target.id, or_(Orders.status=="not_purchased",Orders.status=="processing")).first()
    if not cart:
        try :
            cart = Orders(user_id=target.id, status="not_purchased", total=0,id=str(uuid.uuid4()))
            db.add(cart)
            db.commit()
            db.refresh(cart)
        except SQLAlchemyError:
            raise HTTPException(status_code=400, detail="Invalid Request")
        
    #? カート内の商品を取得
    items = db.query(OrderItems).filter_by(order_id=cart.id).all()
    res = {
        "id": cart.id,
        "status": cart.status,
        "total": cart.total,
        "items": [
            {
                "ticket_id":item.ticket.id,
                "ticket_name":item.ticket.name,
                "ticket_price":item.ticket.price,
                "quantity":item.quantity
            } for item in items 
        ]
    }   

    return res



#! カートに商品を追加
@router.post("/cart/")
def add_ticket_to_cart(ticket_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):

    # ? ユーザとカートを取得
    target = get_user_by_email(db, user["email"])
    
    # ? カートの取得
    cart = db.query(Orders).filter(Orders.user_id==target.id, Orders.status=="not_purchased").first()
    if not cart:
        try :
            cart = Orders(user_id=target.id, status="not_purchased", id=str(uuid.uuid4(),total=0))
            db.add(cart)
            db.commit()
            db.refresh(cart)
        except SQLAlchemyError:
            raise HTTPException(status_code=400, detail="Invalid Request")
        
    # ? チケットの取得
    ticket = db.query(Tickets).filter_by(id=ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # ? カートに商品を追加
    try:
        order_item = db.query(OrderItems).filter_by(order_id=cart.id, ticket_id=ticket.id).first()
        if order_item:
            order_item.quantity += 1
        else:
            order_item = OrderItems(order_id=cart.id, ticket_id=ticket.id, quantity=1)
            db.add(order_item)
        cart.total += ticket.price
        db.commit()
        return {"message": "Ticket added to cart"}
    except SQLAlchemyError:
        raise HTTPException(status_code=400, detail="Invalid Request")
    
    
#! カートから商品を減らす・削除
@router.delete("/cart/")
def delete_ticket_from_cart(ticket_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    #? ユーザを取得
    target = get_user_by_email(db, user["email"])
    
    #? カートを取得
    cart = db.query(Orders).filter(Orders.user_id==target.id,Orders.status=="not_purchased").first()
    
    try : 
        #? カート内の商品を取得
        order_item = db.query(OrderItems).filter_by(order_id=cart.id, ticket_id=ticket_id).first()
        if not order_item:
            raise HTTPException(status_code=404, detail="Ticket not found")
        if order_item.quantity > 1:
            order_item.quantity -= 1
        else:
            db.delete(order_item)
        cart.total -= order_item.ticket.price
        db.commit()
        return {"message": "Ticket added to cart"}
    except SQLAlchemyError:
        raise HTTPException(status_code=400, detail="Invalid Request")