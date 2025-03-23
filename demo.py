import streamlit as st
import openai_api
from prompts import SYSTEM_PROMPT, MSD_DETAILS
import json

# Set the page layout to wide
st.set_page_config(layout="wide")

# Initialize session state for chat history and feedback if not already present
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hello! I am your change management AI assistant. How may I help you?"}
    ]
    st.session_state["feedback"] = []

# Set the title of the Streamlit app
st.title("Change Management Dashboard")

# Create tabs for different sections of the dashboard
tab_chat, tab_feedback, tab_settings = st.tabs(["Chatbot", "Feedback", "Settings"])

# Chatbot tab functionality
with tab_chat:
    # Create a container for chat messages
    chat = st.container(height=600)
    with chat:
        # Display chat history excluding system messages
        for message in st.session_state["chat_history"]:
            if message["role"] == "system":
                continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Handle user input in the chat
    if prompt := st.chat_input("Write a brief description of changing policies or news."):
        with chat:
            # Append user input to chat history
            st.session_state["chat_history"].append({"role": "user", "content": prompt})
            st.chat_message("user").markdown(prompt)

            # Get assistant's reply from OpenAI API and append to chat history
            with st.chat_message("assistant"):
                reply = st.write_stream(openai_api.openai_query_stream(st.session_state["chat_history"]))
                st.session_state["chat_history"].append({"role": "assistant", "content": reply})




# Feedback tab functionality
with tab_feedback:
    # Create columns for data display and analytics
    col_data, col_eda = st.columns([0.6, 0.4])

    # Check if feedback data is available
    if not st.session_state["feedback"]:
        st.write("There are no employee feedbacks in the database! Click the button below to perform feedback forecasting.")
        if st.button("Generate Feedback", type="primary"):
            # Load feedback data from a JSON file
            with open('data/feedback.json', 'r') as file:
                st.session_state["feedback"] = json.load(file)

    # Display feedback data if available
    if st.session_state["feedback"]:
        with col_data:
            # Iterate over feedback entries and display them
            for feedback in st.session_state["feedback"]:
                with st.container(border=True):
                    st.write("Name: " + feedback["name"] + "  | id: " + feedback["id"])
                    st.write("Rating: " + "★" * feedback["rating"])
                    st.write("Feedback: " + feedback["feedback"])

        with col_eda:
            # Display feedback analytics
            st.subheader("Feedback Analytics")
            st.image("figures/pie_chart.jpg", caption="Composition of employee ratings")
            st.image("figures/bar_chart.jpg", caption="Top 4 employee opinions")

            # Provide a summary of employee feedback
            st.markdown("**Employees say:**")
            feedback_summary = (
                "The most common concern is that ChatGPT is difficult to use, followed by a significant number of employees who find it useful. "
                "Some employees worry that it steals personal information, while a smaller group believes it is not relevant in the workplace. "
                "Overall, opinions are mixed, with usability concerns being the most prominent issue."
            )
            st.write(feedback_summary)

            # Send feedback summary to AI assistant for suggestions
            if st.button("Send feedback to AI assistant", type="primary"):
                with tab_chat:
                    with chat:
                        prompt = (
                            f"The following is the general feedback given by employees. Suggest appropriate alterations to the change management policies to improve employee satisfaction. \n\nFeedback:\n{feedback_summary}"
                        )
                        st.session_state["chat_history"].append({"role": "user", "content": prompt})
                        st.chat_message("user").markdown(prompt)

                        # Get assistant's reply from OpenAI API and append to chat history
                        with st.chat_message("assistant"):
                            reply = st.write_stream(openai_api.openai_query_stream(st.session_state["chat_history"]))
                            st.session_state["chat_history"].append({"role": "assistant", "content": reply})




# Settings tab functionality
with tab_settings:
    # Display a text area for MSD details
    st.text_area(
        label="Write a brief description of MSD and its organizational structure:",
        value=MSD_DETAILS.replace("*", ""),
        height=600
    )

    # Button to clear the conversation history
    if st.button("Clear conversation", type="primary"):
        st.session_state["chat_history"] = [{"role": "system", "content": SYSTEM_PROMPT}]