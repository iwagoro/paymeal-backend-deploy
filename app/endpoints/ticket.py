from fastapi import HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from ..schema import TicketSchema
from ..database import Tickets
from .util.util import get_db

router = APIRouter()


# * 画像URLが有効か確認する関数
def validateImageURL(url):
    import requests
    from PIL import Image
    from io import BytesIO

    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img.verify()
        return True
    except:
        return False


#! チケット一覧を取得するエンドポイント (Array)
@router.get("/tickets/", status_code=200)
def get_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Tickets).all()
    if not tickets:
        return Response(status_code=204)
    return tickets


# ? ユーザが管理者のみ実行可能にする必要あり
#! 新しいチケットを追加するエンドポイント
@router.post("/tickets/", status_code=201)
def create_ticket(ticket: TicketSchema, db: Session = Depends(get_db)):
    # 既存のチケットを検索
    existing_ticket = db.query(Tickets).filter_by(name=ticket.name).first()
    if existing_ticket:
        raise HTTPException(status_code=409, detail="Ticket already exists with this name")

    # 画像URLが有効か確認
    if not validateImageURL(ticket.img_url):
        raise HTTPException(status_code=400, detail="Invalid Image URL")

    # 新しいチケットを追加
    new_ticket = Tickets(**ticket.model_dump())
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return "Ticket created"


# ? ユーザが管理者のみ実行可能にする必要あり
#! 既存チケットを削除するエンドポイント
@router.delete("/tickets/{ticket_id}", status_code=201)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    # 既存のチケットが存在するか確認
    ticket = db.query(Tickets).filter_by(id=ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=400, detail="Ticket does not exist with this id")

    # チケットを削除
    db.delete(ticket)
    db.commit()
    return "Ticket deleted"


# ? ユーザが管理者のみ実行可能にする必要あり
#! チケット情報を更新するエンドポイント
@router.put("/tickets/{ticket_id}", status_code=200)
def update_ticket(ticket_id: int, ticket: TicketSchema, db: Session = Depends(get_db)):
    # 既存のチケットが存在するか確認
    existing_ticket = db.query(Tickets).filter_by(id=ticket_id).first()
    if not existing_ticket:
        raise HTTPException(status_code=400, detail="Ticket does not exist with this id")

    # 画像URLが有効か確認
    if not validateImageURL(ticket.img_url):
        raise HTTPException(status_code=400, detail="Invalid Image URL")

    # チケット情報を更新
    existing_ticket.name = ticket.name
    existing_ticket.price = ticket.price
    existing_ticket.description = ticket.description
    existing_ticket.img_url = ticket.img_url
    existing_ticket.stock = ticket.stock
    db.commit()
    return "Ticket updated"
