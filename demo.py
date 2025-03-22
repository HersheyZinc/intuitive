import streamlit as st
import openai_api
from prompts import SYSTEM_PROMPT, MSD_DETAILS
import json

st.set_page_config(layout="wide")

if "chat_history" not in st.session_state:

    st.session_state["chat_history"] = [{"role":"system", "content": SYSTEM_PROMPT}, {"role":"assistant", "content":"Hello! I am your change management AI assistant. How may I help you?"}]
    with open('data/feedback.json', 'r') as file:
        st.session_state["feedback"] = json.load(file)


st.title("Change Management Dashboard")

tab_chat, tab_feedback, tab_settings = st.tabs(["Chatbot", "Feedback", "Settings"])

with tab_chat:

    chat = st.container(height=600)
    with chat:
        for message in st.session_state["chat_history"]:
            if message["role"] == "system":
                continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


    if prompt := st.chat_input("Write a brief description of changing policies or news."):
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
                st.write("Name: " + feedback["name"] + "                  | id: " + feedback["id"])
                st.write("Rating: " + "★" * feedback["rating"])
                st.write("Feedback: " + feedback["feedback"])

    
    with col_eda:
        st.subheader("Feedback Analytics")
        st.image("figures/pie_chart.jpg", caption="Composition of employee ratings")
        st.image("figures/bar_chart.jpg", caption="Top 4 employee opinions")


        st.write("Employees say:")
        st.write("The most common concern is that ChatGPT is difficult to use, followed by a significant number of employees who find it useful. Some employees worry that it steals personal information, while a smaller group believes it is not relevant in the workplace. Overall, opinions are mixed, with usability concerns being the most prominent issue.")


with tab_settings:
    st.text_area(label="Write a brief description of MSD and the organizational structure:", value=MSD_DETAILS, height=600)
    

    if st.button("Clear conversation", type="primary"):
            st.session_state["chat_history"] = [{"role":"system", "content": SYSTEM_PROMPT}]