import streamlit as st
from sqlalchemy.orm import Session
import models
from util.util import get_db
import pandas as pd
import time

def get_orders(db):
    orders = db.query(models.Orders).all()
    return orders

def display_orders():
    db = next(get_db())
    while True:
        orders = get_orders(db)
        st.write("## Orders List")
        df = pd.DataFrame([(order.id, order.status, order.total) for order in orders], columns=["ID", "Status", "Total"])
        tabStrings = ["not_purchased", "purchased", "ordered", "completed"]
        tabs = st.tabs(tabStrings)

        for tabString, tab in zip(tabStrings, tabs):
            with tab:
                st.table(df[df["Status"] == tabString])
        
        # Wait for 5 seconds before updating
        time.sleep(5)
        st.experimental_rerun()

# Run the display function
display_orders()
