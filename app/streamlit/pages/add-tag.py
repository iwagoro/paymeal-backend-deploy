

import streamlit as st
import models
from util.util import get_db
from models import Tags, Tickets,Stocks,TagRelations
from streamlit_pills import pills
from sqlalchemy.exc import IntegrityError



def add_tag_component():
    
    st.title("Add New Tag")

    db = next(get_db())
    tags = db.query(Tags).all()
    tag_names = [tag.name for tag in tags]
    value = pills("",tag_names)
    #? フォーム入力
    tag_name = st.text_input("Tag Name")

    #? タグ追加ボタン
    if st.button("Add Tag"):
        #? タグ名が空でないか確認
        if tag_name != "":
            db = next(get_db())

            try:
                # 新しいタグを作成
                new_tag = Tags(name=tag_name)
                db.add(new_tag)
                db.commit()
                st.success("Tag added successfully!")
            except IntegrityError:
                db.rollback()
                st.error("Tag already exists")
        else :
            st.error("Please enter a tag name")




def display():
    st.set_page_config(layout="wide")
    db = next(get_db())
    add_tag_component()

display()