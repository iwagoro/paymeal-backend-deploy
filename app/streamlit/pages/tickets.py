import streamlit as st
import models
from util.util import get_db
from models import Tags, Tickets, Stocks, TagRelations
from streamlit_pills import pills
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from components.ticket_card import ticket_card
from lib.tickets import add_ticket

def add_ticket_component():
    st.write("## Add New Ticket")

    name = st.text_input("Ticket Name")
    description = st.text_area("Ticket Description")
    contents = st.text_area("Contents (comma separated)").split(",")
    img_url = st.text_input("Image URL")
    price = st.number_input("Price", min_value=0)
    stock = st.number_input("Stock", min_value=0)

    db = next(get_db())
    tags = db.query(Tags).all()
    selected_tags = []
    st.write("Tags")
    for tag in tags:
        if st.checkbox(tag.name, key=f"new_{tag.id}"):
            selected_tags.append(tag.id)

    if st.button("Add Ticket"):
        add_ticket(name, description, contents, img_url, price, stock, selected_tags,db)
        st.success("Ticket added successfully!")
        st.experimental_rerun()  # Rerun to refresh the display

def display_tickets():
    st.set_page_config(layout="wide")

    db = next(get_db())
    tickets = db.query(Tickets, Stocks).join(Stocks, Stocks.ticket_id == Tickets.id).all()
    tags = db.query(Tags).all()

    st.write("## Tickets List")

    # トグルでチケット追加コンポーネントを表示
    with st.expander("Add New Ticket", expanded=False):
        add_ticket_component()

    cols = st.columns(3)  # 3列に分割
    for i, (ticket, stock) in enumerate(tickets):
        col = cols[i % 3]  # チケットを交互に列に割り当て
        with col:
            with st.container():
                outer_cols = st.columns([1, 2])
                with outer_cols[0]:
                    st.image(ticket.img_url)
                with outer_cols[1]:
                    st.header(f"{ticket.name}")
                    st.text(f"{ticket.description}\nPrice: {ticket.price} \nStock: {stock.stock}")

                with st.expander("Edit", expanded=False):
                    ticket_card(ticket, stock, tags,db)

display_tickets()
