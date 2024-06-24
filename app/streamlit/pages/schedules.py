import streamlit as st
from sqlalchemy.orm import Session
from models import Tickets, DailyMenus, TagRelations, Tags
from util.util import get_db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

# データベースセッションの取得
db = next(get_db())

def reset_menu_items():
    st.session_state["menu_items"] = []

def manage_Daily_Menus():
    st.title("Manage Daily Menus")
    st.write("You can add, edit, and delete daily menus here")
    
    # 'daily'タグが付いたチケットを取得
    daily_tickets = db.query(Tickets).join(TagRelations).join(Tags).filter(Tags.name == "daily").all()
    
    ticket_options = {ticket.name: ticket.id for ticket in daily_tickets}
    selected_ticket_name = st.selectbox("Select a daily menu", list(ticket_options.keys()), key="selected_ticket_name", on_change=reset_menu_items)
    
    date = st.date_input("Date", key="selected_date", on_change=reset_menu_items)
    
    if "menu_items" not in st.session_state:
        st.session_state["menu_items"] = []
    
    selected_ticket_id = ticket_options[selected_ticket_name]
    exist_menu = db.query(DailyMenus).filter(and_(DailyMenus.ticket_id == selected_ticket_id, DailyMenus.date == date)).first()
    
    if exist_menu:
        if not st.session_state["menu_items"]:
            st.session_state["menu_items"] = exist_menu.contents["menu"]
    else:
        if not st.session_state["menu_items"]:
            st.session_state["menu_items"] = []

    # フォームの表示
    for i, menu_item in enumerate(st.session_state["menu_items"]):
        st.session_state["menu_items"][i] = st.text_input(f"Menu Item {i+1}", value=menu_item, key=f"menu_item_{i}")
    
    col1, col2 = st.columns([0.1, 0.1])
    with col1:
        if st.button("Add Item"):
            st.session_state["menu_items"].append("")
            st.rerun()
    with col2:
        if st.button("Remove Item"):
            if st.session_state["menu_items"]:
                st.session_state["menu_items"].pop()
                st.rerun()

    # メニューを保存する処理
    if st.button("Save Menu"):
        if exist_menu:
            try:
                db.query(DailyMenus).filter(and_(DailyMenus.ticket_id == selected_ticket_id, DailyMenus.date == date)).update({"contents": {"menu": st.session_state["menu_items"]}})
                db.commit()
                st.success("Menu updated successfully!")
            except SQLAlchemyError as e:
                db.rollback()
                st.error(f"Failed to update menu: {e}") 
        else:
            new_menu = DailyMenus(ticket_id=selected_ticket_id, date=date, contents={"menu": st.session_state["menu_items"]})
            try:
                db.add(new_menu)
                db.commit()
                st.success("Menu created successfully!")
            except SQLAlchemyError as e:
                db.rollback()
                st.error(f"Failed to create menu: {e}")
        
    # メニューを削除する処理
    if st.button("Delete Menu"):
        if exist_menu:
            try:
                db.query(DailyMenus).filter(and_(DailyMenus.ticket_id == selected_ticket_id, DailyMenus.date == date)).delete()
                db.commit()
                st.success("Menu deleted successfully!")
                st.session_state["menu_items"] = []
                st.rerun()
            except SQLAlchemyError as e:
                db.rollback()
                st.error(f"Failed to delete menu: {e}")

# Streamlitアプリケーションの実行
manage_Daily_Menus()
