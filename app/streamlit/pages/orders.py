import streamlit as st
from sqlalchemy.orm import Session
import models

def display_orders(db: Session):
    orders = db.query(models.Orders).all()
    st.write("## Orders List")
    for order in orders:
        st.write(f"ID: {order.id}, Status: {order.status}, Total: {order.total}")
