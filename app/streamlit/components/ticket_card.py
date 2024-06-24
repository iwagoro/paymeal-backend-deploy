from components.tags import tag_component
from lib.tickets import update_ticket
import streamlit as st
from util.util import get_db

def ticket_card(ticket, stock, tags,db):
    new_name = st.text_input("Name", value=ticket.name, key=f"name_{ticket.id}")
    new_description = st.text_area("Description", value=ticket.description, key=f"description_{ticket.id}")
    new_price = st.number_input("Price", value=ticket.price, key=f"price_{ticket.id}")
    new_stock = st.number_input("Stock", value=stock.stock, key=f"stock_{ticket.id}")

    selected_tags = tag_component(ticket, tags)

    if st.button("Update", key=f"update_{ticket.id}"):
        try:
            update_ticket(ticket, stock, new_name, new_description, new_price, new_stock, selected_tags,db)
            st.success("Ticket updated successfully!")
            st.experimental_rerun()  # Rerun to refresh the display
        except Exception as e:
            st.error(f"Error updating ticket: {e}")
