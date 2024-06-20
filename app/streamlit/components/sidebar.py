import streamlit as st

def render_sidebar():
    page = st.sidebar.radio("Navigation", ["Dashboard", "Tickets", "Orders"])
    return page
