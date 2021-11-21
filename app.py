import streamlit as st
from multiapp import MultiApp
import lf, sth, about # import your app modules here

st.set_page_config(page_title="LF & STH Data Explorer", page_icon="💾",
                   layout="wide", initial_sidebar_state="expanded")

#get rid of the side spaces
padding = 1.5
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)

#let's hide the menu
hide_menu="""
<style>
#MainMenu{
    visibility:hidden;
}
footer{visibility:hidden;
}
</style>
"""
st.markdown(hide_menu,unsafe_allow_html=True)

app = MultiApp()


# Add all your application here
with st.sidebar:
    app.add_app("About", about.app)
    app.add_app("Soil Transmitted Helminthiasis", sth.app)
    app.add_app("Lymphatic Filariasis", lf.app)

# The main app
app.run()
