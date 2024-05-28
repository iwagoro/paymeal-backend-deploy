from fastapi import HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from models import Tickets, Tags, TicketTags
from util.util import get_db, create_response, create_error_response
from schema import ResponseModel
import requests
from PIL import Image
from io import BytesIO
from fastapi.encoders import jsonable_encoder

router = APIRouter()


#! 全てのTicket取得
@router.get("/tickets")
def get_all_tickets(db: Session = Depends(get_db)):
    # ? チケットを全て取得
    tickets = db.query(Tickets).all()
    if not tickets:
        raise HTTPException(status_code=404, detail="No tickets found")

    return {"tickets": tickets}


#! Tag取得
@router.get("/tags")
def get_tags(db: Session = Depends(get_db)):
    # ? タグを全て取得
    tags = db.query(Tags).all()
    if not tags:
        raise HTTPException(status_code=404, detail="No tags found")

    return {"tags": tags}


#! ticketとtagの関連を取得
@router.get("/relations")
def get_relations(db: Session = Depends(get_db)):
    # ? タグを全て取得
    relations = db.query(TicketTags).all()
    if not relations:
        raise HTTPException(status_code=404, detail="No relations found")

    return {"relations": relations}
