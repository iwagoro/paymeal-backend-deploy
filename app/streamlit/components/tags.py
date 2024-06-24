import streamlit as st

def tag_component(ticket, tags):
    selected_tags = []
    st.write("Tags")
    for tag in tags:
        isChecked = False
        for tag_relation in ticket.tags:
            if tag.id == tag_relation.tag_id:
                isChecked = True
        if st.checkbox(tag.name, value=isChecked, key=f"{tag.name}_{ticket.id}"):
            selected_tags.append(tag.id)  # Return tag.id instead of tag object
    return selected_tags
