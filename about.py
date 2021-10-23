#import the necessary libraries
import streamlit as st
from PIL import Image

def app():
    st.title('Lymphatic Filariasis (LF) and Soil Transmitted Helminthiasis (STH) Data Explorer')

    st.markdown("""
    ### 👋🏾  Hello there!

    Welcome to the LF and STH data explorer! 🎉🎅🏾🎈

    This app allows you to explore LF and STH data as provided by the mighty 🤭 World Health Organization (WHO). The data is displayed more or less as is. The data used in the app is from **WHO's** [PC Data bank](https://www.who.int/teams/control-of-neglected-tropical-diseases/preventive-chemotherapy/pct-databank/lymphatic-filariasis)
    """)
    st.markdown("### I'm sold! How can I use the app? 😗")
    st.markdown("""
    Excellent! That's the easy part. Follow the following easy steps 😎
    - Click on the drop down on the left side 👈🏾
    - Select the disease you want to explore 🕵🏾‍♀️
    - That's it 💁🏽
    """)
    st.markdown('### Before you go👇🏾')
    st.info("""
    Disclaimer from WHO 🙄: Unless otherwise specified, the preventive chemotherapy database reports information as provided by countries through World Health Organization reporting processes. All reasonable precautions have been taken to verify the information contained in this publication. In no event shall the World Health Organization be liable for damages arising from its use.
    """)
