from fastapi import  HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import  Users , Orders , OrderItems , Tickets
from fastapi import APIRouter
from ..database import SessionClass
import uuid

router = APIRouter()

# データベースセッションを作成する依存関係
def get_db():
    db = SessionClass()
    try:
        yield db
    finally:
        db.close()
        
        
#ユーザのカートの商品一覧を取得するエンドポイント
@router.get("/carts/{user_id}")
def get_carts(user_id: int, db: Session = Depends(get_db)):
    # ユーザーが存在するか確認
    user = db.query(Users).filter_by(id=user_id).first()
    if not user:
        # ユーザーが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User not found")

    # ユーザーのカートを取得
    cart = db.query(Orders).filter_by(user_id=user_id, status="not_purchased").first()
    if not cart:
        # カートが存在しない場合は空のリストを返す
        return []

    # カートのアイテムを取得
    cart_items = db.query(OrderItems).filter_by(order_id=cart.id).all()
    return cart_items

#カートに商品を追加するエンドポイント（すでに存在する場合はインクリメント）
@router.post("/carts/{user_id}/{ticket_id}", response_model=str)
def add_ticket_to_cart(user_id: int, ticket_id: int, db: Session = Depends(get_db)):
    # ユーザーとチケットが存在するか確認
    user = db.query(Users).filter_by(id=user_id).first()
    if not user:
        # ユーザーが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User not found")

    ticket = db.query(Tickets).filter_by(id=ticket_id).first()
    if not ticket:
        # チケットが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="Ticket not found")

    # カートを検索
    cart = db.query(Orders).filter_by(user_id=user_id, status="not_purchased").first()
    if not cart:
        # カートが存在しない場合は新しいカートを作成
        cart = Orders(id=str(uuid.uuid4()), user_id=user_id, status="not_purchased")
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
    db.refresh(cart_item)
    return "Ticket added to cart"

#カートの商品の個数を1個減らすエンドポイント（0個になった場合は削除）
@router.delete("/carts/{user_id}/{ticket_id}", response_model=str)
def remove_ticket_from_cart(user_id: int, ticket_id: int, db: Session = Depends(get_db)):
    # ユーザーとチケットが存在するか確認
    user = db.query(Users).filter_by(id=user_id).first()
    if not user:
        # ユーザーが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User not found")

    ticket = db.query(Tickets).filter_by(id=ticket_id).first()
    if not ticket:
        # チケットが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="Ticket not found")

    # カートを検索
    cart = db.query(Orders).filter_by(user_id=user_id, status="not_purchased").first()
    if not cart:
        # カートが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="Cart not found")

    cart_item = db.query(OrderItems).filter_by(order_id=cart.id, ticket_id=ticket_id).first()
    if not cart_item:
        # カートアイテムが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="Ticket not in cart")

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        db.delete(cart_item)

    db.commit()
    return "Ticket removed from cart"