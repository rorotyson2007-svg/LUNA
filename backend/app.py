import streamlit as st
import sys
sys.path.append("backend")  # so you can import your existing modules

from app.whatever_module import your_function  # adjust to your actual logic

st.title("LUNA")

user_input = st.text_input("Enter something")

if st.button("Run"):
    result = your_function(user_input)  # call your actual logic
    st.write(result)