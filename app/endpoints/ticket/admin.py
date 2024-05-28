from fastapi import HTTPException, Depends, APIRouter, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from schema import TicketSchema, TagSchema, TicketTagSchema
from models import Tickets, AdminUsers, Tags, TicketTags
from util.util import get_db, verify_token, create_response, create_error_response
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi.encoders import jsonable_encoder
import requests
from PIL import Image
from io import BytesIO

router = APIRouter()


# * 画像URLが有効か確認
def validateImageURL(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img.verify()
        return True
    except:
        return False


# * ユーザを確認する関数
def get_user_by_email(db: Session, email: str):
    user = db.query(AdminUsers).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    return user


#! タグ追加
@router.post("/tags")
def create_tag(tag: TagSchema, user=Depends(verify_token), db: Session = Depends(get_db)):
    # ?管理者の確認
    target = get_user_by_email(db, user["email"])

    try:
        # ? 新しいタグを追加
        new_tag = Tags(**tag.model_dump())
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return Response(status_code=201)
    # ? 重複エラー
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="Tag already exists") from e
    # ? その他のエラー
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Invalid Request")


#! タグの関連付け
@router.post("/tickets/{ticket_id}", status_code=201)
def create_tag_relation(
    ticket_id: int, tags: TicketTagSchema, user=Depends(verify_token), db: Session = Depends(get_db)
):

    # ?管理者の確認
    target = get_user_by_email(db, user["email"])

    # ? 既存のチケットを検索
    existing_ticket = db.query(Tickets).filter_by(id=ticket_id).first()
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="TICKET NOT FOUND")
    # ? チケットに関連づけられたタグを全て削除
    db.query(TicketTags).filter_by(ticket_id=ticket_id).delete()
    # ? "all"タグを削除
    if "all" in tags.tags:
        tags.tags.remove("all")
    try:
        # ? 新しいタグを追加
        for tag in tags.tags:
            existing_tag = db.query(Tags).filter_by(name=tag).first()
            if not existing_tag:
                raise HTTPException(status_code=404, detail="TAG NOT FOUND")
            new_relation = TicketTags(ticket_id=ticket_id, tag_id=existing_tag.id)
            db.add(new_relation)
        db.commit()
        db.refresh(new_relation)
        return Response(status_code=201)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="INVALID REQUEST")


#! 食券の追加
@router.post("/tickets")
def create_ticket(ticket: TicketSchema, user=Depends(verify_token), db: Session = Depends(get_db)):
    # ?管理者の確認
    target = get_user_by_email(db, user["email"])

    # ? 画像URLが有効か確認
    if not validateImageURL(ticket.img_url):
        raise HTTPException(status_code=400, detail="INVALID IMAGE")

    try:
        # ? 新しいチケットを追加
        new_ticket = Tickets(**ticket.model_dump())
        db.add(new_ticket)
        db.commit()
        return Response(status_code=201)

    # ? 重複エラー
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="Tag already exists") from e
    # ? その他のエラー
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Invalid Request")


#! 食券の削除
@router.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int, user=Depends(verify_token), db: Session = Depends(get_db)):
    # ?管理者の確認
    target = get_user_by_email(db, user["email"])

    # ? 既存のチケットを検索
    existing_ticket = db.query(Tickets).filter_by(id=ticket_id).first()
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    try:
        # ? チケットを削除
        db.delete(existing_ticket)
        db.commit()
        return Response(status_code=204)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Invalid Request")


#! 食券の更新
@router.put("/tickets/{ticket_id}")
def update_ticket(ticket_id: int, ticket: TicketSchema, user=Depends(verify_token), db: Session = Depends(get_db)):
    # ?管理者の確認
    target = get_user_by_email(db, user["email"])

    # ? 既存のチケットが存在するか確認
    existing_ticket = db.query(Tickets).filter_by(id=ticket_id).first()
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    # ? 画像URLが有効か確認
    if not validateImageURL(ticket.img_url):
        raise HTTPException(status_code=400, detail="INVALID IMAGE")

    try:
        # ? チケット情報を更新
        existing_ticket.name = ticket.name
        existing_ticket.price = ticket.price
        existing_ticket.description = ticket.description
        existing_ticket.img_url = ticket.img_url
        existing_ticket.stock = ticket.stock
        existing_ticket.contents = ticket.contents
        db.commit()
        return Response(status_code=201)

    except SQLAlchemyError as e:
        return create_error_response(code=400, message="INVALID REQUEST")
