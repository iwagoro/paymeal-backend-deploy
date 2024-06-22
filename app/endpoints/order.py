from fastapi import HTTPException, Depends, Response, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from models import Users, Orders, OrderItems
from util.util import get_db, verify_token, get_user_by_email ,get_today,is_orderable_time
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()



#! 最新の注文１件を取得
@router.get("/orders/latest")
def get_latest_order(user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])
    today = get_today() 

    # ? 最新の注文を取得
    order = (
        db.query(Orders)
        .filter(
            Orders.user_id == target.id,
            Orders.status != "not_purchased",
            Orders.status != "processing"
        )
        .order_by(desc(Orders.purchase_date))
        .first()
    )
    if not order:
        raise HTTPException(status_code=204, detail="No orders found")

    #? 注文内容を取得
    tickets = db.query(OrderItems).filter_by(order_id=order.id).all()
    
    res = {
        "id": order.id,
        "status": order.status,
        "total": order.total,
        "purchase_date": order.purchase_date,
        "order_date": order.order_date,
        "number": order.number,
        "items": [{
            "quantity": item.quantity,
            "ticket_id": item.ticket_id,
            "ticket_name": item.ticket.name,
            "ticket_price": item.ticket.price
        } for item in tickets]
    }
    
    return res


#! 全ての注文を取得
@router.get("/orders/all/", status_code=200)
def get_orders(status:str,user=Depends(verify_token), db: Session = Depends(get_db)):
    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])
    print("this is orders all")
    if status != "purchased" and status != "ordered" and status != "completed":
        raise HTTPException(status_code=400, detail="Invalid status request")

    # ? 注文を取得
    orders = (
        db.query(Orders)
        .filter(
            Orders.user_id == target.id,
            Orders.status == status
        )
        .order_by(desc(Orders.purchase_date))
        .all()
    )
    if not orders:
        raise HTTPException(status_code=204, detail="No orders found")
    
    res = [
        {
            "id": order.id,
            "status": order.status,
            "total": order.total,
            "purchase_date": order.purchase_date,
            "order_date": order.order_date,
            "number": order.number,
            
        } for order in orders
    ]
    
    return res

#! 注文の詳細を取得
@router.get("/orders/")
def get_order_detail(order_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):
    #? ユーザを取得
    target = get_user_by_email(db, user["email"])
    
    #? 注文を取得
    order_items = db.query(OrderItems).filter_by(order_id=order_id).all()
    if not order_items:
        raise HTTPException(status_code=404, detail="Order not found")
    
    res = {
        "items": [{
            "quantity": item.quantity,
            "ticket_id": item.ticket_id,
            "ticket_name": item.ticket.name,
            "ticket_price": item.ticket.price
        } for item in order_items]
    }
    
    return {"detail":res}

#! 注文する
@router.post("/orders/", status_code=201)
def create_order(order_id: str, user=Depends(verify_token), db: Session = Depends(get_db)):

    # ? ユーザを取得
    target = get_user_by_email(db, user["email"])
    today = get_today()
    # ? 注文を取得
    order = db.query(Orders).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "purchased":
        raise HTTPException(status_code=400, detail="Invalid order status")
    if not is_orderable_time():
        raise HTTPException(status_code=400, detail="Not orderable time")
    if order.purchase_date != today:
        raise HTTPException(status_code=400, detail="Ticket is expired")
    try:
        order.status = "ordered"
        db.add(order)
        db.commit()
        return Response(status_code=201)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Invalid Request")
