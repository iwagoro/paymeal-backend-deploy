import streamlit as st
import models
from util.util import get_db
from models import Tags, Tickets,Stocks,TagRelations
from streamlit_pills import pills
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from components.ticket_card import ticket_card
import numpy as np


db = next(get_db())

def display_tickets():
    st.set_page_config(layout="wide")

    tickets = db.query(Tickets, Stocks).join(Stocks, Stocks.ticket_id == Tickets.id).all()
    tags = db.query(Tags).all()

    st.write("## Tickets List")

    cols = st.columns(3)  # 3列に分割
    for i, (ticket, stock) in enumerate(tickets):
        col = cols[i % 3]  # チケットを交互に列に割り当て
        with col:
            with st.container(border=True):
                outer_cols = st.columns([1, 2])
                with outer_cols[0]:
                    st.image(ticket.img_url)
                with outer_cols[1]:
                    st.header(f"{ticket.name}")
                    st.text(f"{ticket.description}\nPrice: {ticket.price} \nStock: {stock.stock}")

                with st.expander("Edit", expanded=False):
                    ticket_card(ticket, stock, tags)

                    


display_tickets()