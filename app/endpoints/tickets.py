from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from models import Tickets, TagRelations,Tags,PopularMenus,DailyMenus,Stocks
from fastapi.responses import JSONResponse
from util.util import get_db

router = APIRouter()


#! 全てのタグを取得
@router.get("/tags")
async def get_tags(db: Session = Depends(get_db)):
    # ? 全てのタグを取得
    tags = db.query(Tags).order_by(Tags.id).all()
    # ? レスポンスの作成
    return tags

#! 食券を取得
@router.get("/tickets")
async def get_tickets(db: Session = Depends(get_db)):
    # ? タグを指定して食券を取得
    tickets = db.query(Tickets).order_by(Tickets.id).all()

    res = []

    for ticket in tickets:
        res.append({
            "id": ticket.id,
            "name": ticket.name,
            "description": ticket.description,
            "contents": ticket.contents,
            "img_url": ticket.img_url,
            "price": ticket.price,
            "tags": [tag.tag.name for tag in ticket.tags],
            "stock": 0,
            "sales":0,
        })

    # ? レスポンスの作成
    return res

#! 食券の在庫を取得
@router.get("/stocks")
async def get_stock(db: Session = Depends(get_db)):
    # ? 食券の在庫を取得
    stocks = db.query(Stocks).order_by(Stocks.ticket_id).all()
    # ? レスポンスの作成
    return stocks

#! 日替わりメニューを取得
@router.get("/tickets/daily")
async def get_daily_menus(db: Session = Depends(get_db)):
    # ? 日替わりメニューを取得
    daily_menus = db.query(Tickets).join(DailyMenus).all()
    # ? レスポンスの作成
    return {"tickets": daily_menus}
    
#! 人気メニューを取得
@router.get("/tickets/popular")
async def get_popular_menus(db: Session = Depends(get_db)):
    # ? 人気メニューを取得
    popular_menus = db.query(Tickets).join(PopularMenus).all()
    # ? レスポンスの作成
    return {"tickets": popular_menus}