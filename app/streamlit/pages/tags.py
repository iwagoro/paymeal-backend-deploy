import streamlit as st
import models
from util.util import get_db
from models import Tags, TagRelations
from streamlit_pills import pills
from sqlalchemy.exc import IntegrityError

def add_tag_component():
    st.title("Manage Tags")

    db = next(get_db())
    tags = db.query(Tags).all()
    tag_names = [tag.name for tag in tags]
    
    st.write("### Existing Tags")
    selected_tag = pills("", tag_names)

    if st.button("Delete Tag"):
        if selected_tag:
            db = next(get_db())
            try:
                tag_to_delete = db.query(Tags).filter(Tags.name == selected_tag).one()
                
                # Delete related records in TagRelations
                db.query(TagRelations).filter(TagRelations.tag_id == tag_to_delete.id).delete()
                
                # Now delete the tag
                db.delete(tag_to_delete)
                db.commit()
                st.success("Tag deleted successfully!")
                st.experimental_rerun()  # Rerun to refresh the display
            except Exception as e:
                db.rollback()
                st.error(f"Error deleting tag: {e}")
        else:
            st.error("Please select a tag to delete")

    st.write("### Add New Tag")
    tag_name = st.text_input("Tag Name")

    if st.button("Add Tag"):
        if tag_name:
            db = next(get_db())
            try:
                new_tag = Tags(name=tag_name)
                db.add(new_tag)
                db.commit()
                st.success("Tag added successfully!")
                st.experimental_rerun()  # Rerun to refresh the display
            except IntegrityError:
                db.rollback()
                st.error("Tag already exists")
        else:
            st.error("Please enter a tag name")

def display():
    st.set_page_config(layout="wide")
    add_tag_component()

display()
