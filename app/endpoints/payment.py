from fastapi import  HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import  Users , Orders , OrderItems , Tickets
from fastapi import APIRouter
from ..database import SessionClass
from ..paypay import create_payment , get_payment_details , delete_payment


router = APIRouter()

# データベースセッションを作成する依存関係
def get_db():
    db = SessionClass()
    try:
        yield db
    finally:
        db.close()
        

#カート内の商品を購入するためのQRコードを作成するエンドポイント、statusはprocessingに変更
@router.post("/payment-link/{user_id}", response_model=str)
def create_order(user_id: int, db: Session = Depends(get_db)):
    # ユーザーが存在するか確認
    user = db.query(Users).filter_by(id=user_id).first()
    if not user:
        # ユーザーが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User not found")

    # カートを検索
    cart = db.query(Orders).filter(Orders.user_id == user_id,Orders.status=="not_purchased").first()

    if not cart:
        # カートが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="Cart is empty")

    cart_items = db.query(OrderItems).filter_by(order_id=cart.id).all()

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
    url,code_id = create_payment(cart.id,order_content, total)

    cart.status = "processing"
    cart.code_id = code_id
    cart.payment_link = url
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return url

#QRコードリンクを削除するエンドポイント
@router.delete("/payment-link/{user_id}", response_model=str)
def delete_order(user_id: int, db: Session = Depends(get_db)):
    # ユーザーが存在するか確認
    user = db.query(Users).filter_by(id=user_id).first()
    if not user:
        # ユーザーが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User not found")

    # カートを検索
    cart = db.query(Orders).filter_by(user_id=user_id, status="processing").first()
    if not cart:
        # カートが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="Cart not found")
    
    code_id = cart.code_id
    state = delete_payment(code_id)
    
    if state == "SUCCESS":
        cart.status = "not_purchased"
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return "Order canceled"

    else :
        raise HTTPException(status_code=400, detail="Payment not canceled")
    

# 決済が完了したか確認するエンドポイント
@router.post("/payment-status/{user_id}", response_model=str)
def complete_purchase(user_id: int, db: Session = Depends(get_db)):
    # ユーザーが存在するか確認
    user = db.query(Users).filter_by(id=user_id).first()
    if not user:
        # ユーザーが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User not found")

    # カートを検索
    cart = db.query(Orders).filter_by(user_id=user_id, status="processing").first()
    if not cart:
        # カートが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="Cart not found")
    
    state = get_payment_details(cart.id)
    print(state)
    
    if state == "SUCCESS":
        cart.status = "purchased"
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return "Purchase completed"

    else : 
        raise HTTPException(status_code=400, detail="Payment not completed")

# 決済をキャンセルするエンドポイント
@router.delete("/payment-status/{user_id}", response_model=str)
def cancel_purchase(user_id: int, db: Session = Depends(get_db)):
    # ユーザーが存在するか確認
    user = db.query(Users).filter_by(id=user_id).first()
    if not user:
        # ユーザーが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User not found")
    
    # カートを検索
    cart = db.query(Orders).filter_by(user_id=user_id, status="processing").first()
    if not cart:
        # カートが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="Cart not found")
    
    id = cart.id
    state = delete_payment(id)
    
    if state == "SUCCESS":
        cart.status = "not_purchased"
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return "Purchase canceled"
    
    else :
        raise HTTPException(status_code=400, detail="Payment not canceled")