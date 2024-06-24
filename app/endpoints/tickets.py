from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from models import OrderItems, Orders, Tickets, TagRelations,Tags,PopularMenus,Stocks,DailyMenus
from fastapi.responses import JSONResponse
from util.util import get_db,get_today
import pandas as pd
from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

#* 人気メニューを計算して更新
def calculate_and_update_popular_menus(db: Session, today):
    one_week_ago = today - timedelta(days=7)
    one_week_orders = (
        db.query(OrderItems)
        .join(Orders, OrderItems.order_id == Orders.id)
        .filter(Orders.purchase_date >= one_week_ago)
        .all()
    )
    
    # DataFrameの作成
    df = pd.DataFrame([(order.ticket_id, order.quantity) for order in one_week_orders], columns=["ticket_id", "quantity"])
    
    # ticket_idごとのquantityを集計
    grouped_df = df.groupby('ticket_id')['quantity'].sum().reset_index()
    
    # quantityでソートして上位5件を取得
    ranking = grouped_df.sort_values('quantity', ascending=False).head(5)
    
    popular_menus = []
    for index, row in ranking.iterrows():
        popular_ticket_id = int(row["ticket_id"])
        popular_menus.append(PopularMenus(ticket_id=popular_ticket_id, ranking=index+1, date=today))
    
    try:
        db.add_all(popular_menus)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid Request: {e}")
    
    return popular_menus

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
    # 日替わりメニューを取得
    daily_menus = db.query(Tickets, DailyMenus).join(DailyMenus, Tickets.id == DailyMenus.ticket_id).all()
    
    # 結合した結果をJSON形式で返す
    result = []
    for ticket, daily_menu in daily_menus:
        result.append({
            "id": ticket.id,
            "name": ticket.name,
            "img_url": ticket.img_url,  
            "description": ticket.description,
            "date": daily_menu.date,
            "contents": daily_menu.contents["menu"]
        })
    
    return result

#! 人気メニューを取得
@router.get("/tickets/popular")
async def get_popular_menus(db: Session = Depends(get_db)):
    today = get_today()

    # 今日の日付でエントリが存在するかを確認
    existing_popular_menus = db.query(PopularMenus).filter(PopularMenus.date == today).all()
    if existing_popular_menus:
        popular_tickets = db.query(Tickets).join(PopularMenus, Tickets.id == PopularMenus.ticket_id).all()
        return popular_tickets

    # 今日の日付でエントリが存在しない場合は計算し直す
    calculate_and_update_popular_menus(db, today)
    
    popular_tickets = db.query(Tickets).join(PopularMenus, Tickets.id == PopularMenus.ticket_id).all()
    return popular_tickets