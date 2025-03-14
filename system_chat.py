import streamlit as st
from swarm_agents import app
import re
import json
import time
import uuid

# Set page configuration
st.set_page_config(
    page_title="Water Consumption and Awareness building Assistant", layout="wide"
)


# Function to generate and store a unique User ID (U-ID)
def get_user_id():
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())  # Generate a unique ID
    return st.session_state.user_id


# Function to format AI response
def format_response(response_text):
    response_text = response_text.replace("\\n\\n", "\\n")
    response_text = response_text.replace("\\n", "<br>")
    return response_text


# Adjust layout to remove extra white space
st.markdown(
    """
    <style>
        .block-container { padding-top: 20px !important; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='font-size: 25px;'>Water Consumption and Awareness building Assistant 🤖</h1>",
    unsafe_allow_html=True,
)

chart_url = "https://dataplatform.cloud.ibm.com/dataview/visualizations/e531dac0-a65a-40f2-8e07-87b6d5c6e88c/exports/default?project_id=df19bec2-95cf-45f4-a536-1cd2af15b881&export_type=html"
st.markdown(f"[Click here to view the chart 🔗]({chart_url})", unsafe_allow_html=True)

# Initialize chat history
if "chat_history" not in st.session_state:
    welcome_message = "Welcome to Water Consumption and Awareness building Assistant! How can I help you today?"
    st.session_state.chat_history = [("assistant", welcome_message)]


# Extract latest Human and AI messages
def extract_relevant_messages(message_obj):
    if not isinstance(message_obj, str):
        try:
            message_str = json.dumps(message_obj)
        except Exception:
            message_str = str(message_obj)
    else:
        message_str = message_obj

    human_matches = re.findall(r"HumanMessage\(content='(.*?)'", message_str, re.DOTALL)
    ai_matches = re.findall(
        r"AIMessage\(content=['\"](.*?)['\"],", message_str, re.DOTALL
    )

    last_human_message = human_matches[-1] if human_matches else None
    last_ai_message = ai_matches[-1] if ai_matches else None

    return last_human_message, last_ai_message


# Chat Function
def chat():
    # Display chat history
    for message in st.session_state.chat_history:
        role, content = message
        with st.chat_message(role):
            st.markdown(content, unsafe_allow_html=True)

    # Capture user input
    user_input = st.chat_input("Ask a question...")

    # Dynamic U-ID for each user
    user_id = get_user_id()

    # Generate dynamic config per user
    config = {"configurable": {"thread_id": user_id}}

    # Handle user input
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

        # Invoke the RAG Agent
        with st.spinner("Thinking..."):
            response = app.invoke(
                {"messages": [{"role": "user", "content": user_input}]}, config=config
            )
            user_message, final_ai_message = extract_relevant_messages(response)

            # Display AI response
            if final_ai_message:
                try:
                    final_ai_message = str(final_ai_message)
                    formatted_ai_response = format_response(final_ai_message)
                except Exception as e:
                    st.error(f"Error processing AI response: {str(e)}")
                    formatted_ai_response = (
                        "Sorry, I encountered an error while processing the response."
                    )

                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    streamed_response = ""

                    # Stream response word by word
                    for word in formatted_ai_response.split():
                        streamed_response += word + " "
                        message_placeholder.markdown(
                            streamed_response, unsafe_allow_html=True
                        )
                        time.sleep(0.02)

                st.session_state.chat_history.append(("assistant", streamed_response))


if __name__ == "__main__":
    chat()
