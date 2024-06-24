import streamlit as st

import sys
sys.path.append("/workspace/app")

from database import init_db

# データベースの初期化
init_db()


