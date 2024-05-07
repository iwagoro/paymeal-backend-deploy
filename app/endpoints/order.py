from fastapi import  HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import  Users , Orders , OrderItems , Tickets
from ..schema import UserId , Cart , OrderInfo
from fastapi import APIRouter , WebSocket   
from ..database import SessionClass

router = APIRouter()

# データベースセッションを作成する依存関係
def get_db():
    db = SessionClass()
    try:
        yield db
    finally:
        db.close()
        
        
# 過去の購入履歴を取得するエンドポイント
@router.post("/orders")
def get_orders(user_id: UserId, db: Session = Depends(get_db)):
    # ユーザーが存在するか確認
    user = db.query(Users).filter_by(id=user_id.id).first()
    if not user:
        # ユーザーが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User not found")

    # ユーザーの過去の注文を取得
    orders = db.query(Orders).filter_by(user_id=user_id.id).all()
    if not orders:
        # 注文が存在しない場合は空のリストを返す
        return []
    
    # 注文のアイテムを取得
    order_items = []
    for order in orders:
        items = db.query(OrderItems).filter_by(order_id=order.id).all()
        order_items.append({"order": order, "items": items})
    return order_items

# 注文を作成するエンドポイント
@router.post("/placing_order/")
def create_order(info:OrderInfo, db: Session = Depends(get_db)):
    # ユーザーが存在するか確認
    user = db.query(Users).filter_by(id=info.user_id).first()
    if not user:
        # ユーザーが存在しない場合は 400 エラーを返す
        raise HTTPException(status_code=400, detail="User not found")
    
    order = db.query(Orders).filter_by(id=info.order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")
    
    if order.status != "purchased":
        if order.status == "ordered":
            raise HTTPException(status_code=400, detail="Order is already created")
        
        elif order.status == "completed":
            raise HTTPException(status_code=400, detail="Order is already completed")
        
        else:
            raise HTTPException(status_code=400, detail="Order is not purchased")
    
    order.status = "ordered"
    db.commit()
    return "Order created"



# 注文が完了したときに通知を送信するエンドポイント
@router.websocket("/notification")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")