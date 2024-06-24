
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from models import Tags, Tickets, Stocks, TagRelations
from util.util import get_db
import streamlit as st



def update_ticket(ticket, stock, new_name, new_description, new_price, new_stock, selected_tags,db):
    try:
        ticket.name = new_name
        ticket.description = new_description
        ticket.price = new_price
        stock.stock = new_stock
        
        # Delete existing tag relations
        db.query(TagRelations).filter(TagRelations.ticket_id == ticket.id).delete()

        # Add new tag relations
        for tag_id in selected_tags:
            tag_relation = TagRelations(ticket_id=ticket.id, tag_id=tag_id)
            db.add(tag_relation)
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise e



def add_ticket(name, description, contents, img_url, price, stock, selected_tags,db):
    try:
        new_ticket = Tickets(
            name=name,
            description=description,
            contents=contents,
            img_url=img_url,
            price=price
        )
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)

        new_stock = Stocks(
            ticket_id=new_ticket.id,
            stock=stock,
            unit_sales=0
        )
        db.add(new_stock)

        for tag_id in selected_tags:
            new_relation = TagRelations(ticket_id=new_ticket.id, tag_id=tag_id)
            db.add(new_relation)
        db.commit()

        st.success("Ticket added successfully!")
    except SQLAlchemyError:
        db.rollback()
        st.error("Failed to add ticket or tags")
