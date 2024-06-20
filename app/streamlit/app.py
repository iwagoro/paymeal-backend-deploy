import streamlit as st

import sys
sys.path.append("/workspace/app")
print(sys.path)

from database import init_db
from components.sidebar import render_sidebar
from pages.dashboard import display_dashboard
from pages.tickets import display_tickets
from pages.orders import display_orders
from util.util import get_db


# データベースの初期化
init_db()

# Streamlitアプリケーションの設定
def main():
    st.title("Admin Dashboard")


if __name__ == "__main__":
    main()
