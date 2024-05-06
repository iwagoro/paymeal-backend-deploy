from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .schema import Ticket, User, Order, OrderItem
from .database import Tickets, Users, SessionClass, Orders, OrderItems
from fastapi.middleware.cors import CORSMiddleware
from .paypay import create_payment
import uuid
from mangum import Mangum

# FastAPI のアプリケーションを作成
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# データベースセッションを作成する依存関係
def get_db():
    db = SessionClass()
    try:
        yield db
    finally:
        db.close()


##########---USER---##########################################################


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(Users).all()


@app.post("/users", response_model=str)
def create_user(user: User, db: Session = Depends(get_db)):
    # 既存のユーザーを検索
    existing_user = db.query(Users).filter_by(email=user.email).first()
    if existing_user:
        # ユーザーがすでに存在する場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User already exists with this email")

    # 新しいユーザーを追加
    new_user = Users(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return "User created"


##########---TICKET---##########################################################


# チケット一覧を取得するエンドポイント
@app.get("/tickets/")
def get_tickets(db: Session = Depends(get_db)):
    return db.query(Tickets).all()


# 新しいチケットを追加するエンドポイント
@app.post("/tickets/", response_model=str)
def create_ticket(ticket: Ticket, db: Session = Depends(get_db)):
    # 既存のチケットを検索
    existing_ticket = db.query(Tickets).filter_by(name=ticket.name).first()
    if existing_ticket:
        # チケットがすでに存在する場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="Ticket already exists with this name")

    # 新しいチケットを追加
    new_ticket = Tickets(**ticket.model_dump())
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return "Ticket created"


##########---CART---##########################################################
@app.get("/carts/{user_id}")
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


@app.post("/carts/{user_id}/{ticket_id}", response_model=str)
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


@app.post("/create_order/{user_id}", response_model=str)
def create_order(user_id: int, db: Session = Depends(get_db)):
    # ユーザーが存在するか確認
    user = db.query(Users).filter_by(id=user_id).first()
    if not user:
        # ユーザーが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User not found")

    # カートを検索
    cart = db.query(Orders).filter_by(user_id=user_id, status="not_purchased").first()
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
    url = create_payment(order_content, total)

    cart.status = "purchased"
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return url


@app.post("/complete_purchase/{user_id}", response_model=str)
def complete_purchase(user_id: int, db: Session = Depends(get_db)):
    # ユーザーが存在するか確認
    user = db.query(Users).filter_by(id=user_id).first()
    if not user:
        # ユーザーが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User not found")

    # カートを検索
    cart = db.query(Orders).filter_by(user_id=user_id, status="purchased").first()
    if not cart:
        # カートが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="Cart not found")

    cart.status = "purchased"
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return "Purchase completed"


@app.get("/orders/{user_id}")
def get_orders(user_id: int, db: Session = Depends(get_db)):
    # ユーザーが存在するか確認
    user = db.query(Users).filter_by(id=user_id).first()
    if not user:
        # ユーザーが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User not found")

    # ユーザーの注文を取得
    orders = db.query(Orders).filter_by(user_id=user_id, status="purchased").all()
    return orders


# 1.フロントから購入りクエストを送る
# 2.バックエンドがPaypayのQRコードを生成し、それを返す status: pending
# 3.フロントエンドがPaypayのQRコードから決済処理
# 4.決済ページからリダイレクトされたら、バックエンドにりクエスト
# 5.バックエンドが注文を完了する　status: completed


handler = Mangum(app)
