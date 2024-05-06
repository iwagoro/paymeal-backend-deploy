from fastapi import  HTTPException, Depends
from sqlalchemy.orm import Session
from ..schema import  Ticket
from ..database import  Tickets
from fastapi import APIRouter
from ..database import SessionClass

router = APIRouter()

# データベースセッションを作成する依存関係
def get_db():
    db = SessionClass()
    try:
        yield db
    finally:
        db.close()

# チケット一覧を取得するエンドポイント
@router.get("/tickets/")
def get_tickets(db: Session = Depends(get_db)):
    return db.query(Tickets).all()


# 新しいチケットを追加するエンドポイント
@router.post("/tickets/", response_model=str)
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


# 既存チケットを削除するエンドポイント
@router.delete("/tickets/{ticket_id}", response_model=str)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    # 既存のチケットが存在するか確認
    ticket = db.query(Tickets).filter_by(id=ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=400, detail="Ticket does not exist with this id")
    
    # チケットを削除
    db.delete(ticket)
    db.commit()
    return "Ticket deleted"


# チケット情報を更新するエンドポイント
@router.put("/tickets/{ticket_id}", response_model=str)
def update_ticket(ticket_id: int, ticket: Ticket, db: Session = Depends(get_db)):
    # 既存のチケットが存在するか確認
    existing_ticket = db.query(Tickets).filter_by(id=ticket_id).first()
    if not existing_ticket:
        raise HTTPException(status_code=400, detail="Ticket does not exist with this id")
    
    # チケット情報を更新
    existing_ticket.name = ticket.name
    existing_ticket.price = ticket.price
    existing_ticket.description = ticket.description
    existing_ticket.img_url = ticket.img_url
    existing_ticket.stock = ticket.stock
    db.commit()
    return "Ticket updated"