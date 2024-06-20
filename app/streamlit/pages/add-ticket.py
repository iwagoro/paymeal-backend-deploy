import streamlit as st
import models
from util.util import get_db
from models import Tags, Tickets,Stocks,TagRelations
from streamlit_pills import pills
from lib.tickets import add_ticket

db = next(get_db())

def add_ticket_component():
    st.write("## Add New Ticket")

    name = st.text_input("Ticket Name")
    description = st.text_area("Ticket Description")
    contents = st.text_area("Contents (comma separated)").split(",")
    img_url = st.text_input("Image URL")
    price = st.number_input("Price", min_value=0)
    stock = st.number_input("Stock", min_value=0)

    tags = db.query(Tags).all()
    selected_tags = []
    st.write("Tags")
    for tag in tags:
        if st.checkbox(tag.name, key=f"new_{tag.id}"):
            selected_tags.append(tag.id)

    if st.button("Add Ticket"):
        add_ticket(name, description, contents, img_url, price, stock, selected_tags)


def display_tickets():
    st.set_page_config(layout="wide")
    db = next(get_db())

    ticket = db.query(Tickets).all()
    add_ticket_component()
                    


display_tickets()