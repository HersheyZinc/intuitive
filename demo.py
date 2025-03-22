import streamlit as st
import openai_api
from prompts import SYSTEM_PROMPT, MSD_DETAILS
import json

st.set_page_config(layout="wide")

if "chat_history" not in st.session_state:

    st.session_state["chat_history"] = [{"role":"system", "content": SYSTEM_PROMPT}]
    with open('data/feedback.json', 'r') as file:
        st.session_state["feedback"] = json.load(file)


st.title("Change Management Assistant")

tab_chat, tab_feedback, tab_settings = st.tabs(["Chatbot", "Feedback", "Settings"])

with tab_chat:

    chat = st.container(height=600)
    with chat:
        for message in st.session_state["chat_history"]:
            if message["role"] == "system":
                continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


    if prompt := st.chat_input("Ask me a question on change management!"):
        with chat:
            st.session_state["chat_history"].append({"role":"user", "content": prompt})
            st.chat_message("user").markdown(prompt)


            reply = openai_api.openai_query(st.session_state["chat_history"])
            st.session_state["chat_history"].append({"role":"assistant", "content": reply})
            st.chat_message("assistant").markdown(reply)


with tab_feedback:
    col_data, col_eda = st.columns([0.6, 0.4])

    with col_data:

        for feedback in st.session_state["feedback"]:
            with st.container(border=True):
                st.write("Name: " + feedback["name"] + "    id: " + feedback["id"])
                st.write("Rating: " + "★" * feedback["rating"])
                st.write("Feedback: " + feedback["feedback"])

    
    with col_eda:
        
        st.markdown("Common topics:")
        st.markdown("")


with tab_settings:
    st.write("Write a brief description of MSD and the organizational structure:")
    st.text_area()

    if st.button("Clear conversation"):
            st.session_state["chat_history"] = [{"role":"system", "content": SYSTEM_PROMPT}]