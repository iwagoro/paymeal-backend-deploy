import streamlit as st

def custom_card(title, description, left_content, right_content, image_url=None):
    st.markdown(
        """
        <style>
        .card {
            padding: 20px;
            margin: 10px 0;
            border-radius: 10px;
            background-color: #f9f9f9;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .card img {
            width: 100%;
            border-radius: 10px;
        }
        .card .row {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }
        .card .column {
            flex: 50%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        if image_url:
            st.markdown(f'<img src="{image_url}" alt="Card image">', unsafe_allow_html=True)
        
        st.markdown(f'<h2>{title}</h2>', unsafe_allow_html=True)
        st.markdown(f'<p>{description}</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="row">', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="column">', unsafe_allow_html=True)
            left_content()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="column">', unsafe_allow_html=True)
            right_content()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
