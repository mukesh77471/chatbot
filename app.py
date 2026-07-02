import streamlit as str
import google.generativeai as genai

# Configure the page
str.set_page_config(page_title="Free Chatbot", page_icon="🤖")
str.title("🤖 My Free AI Assistant")

# Securely fetch the API key (Streamlit Secrets handles this in deployment)
api_key = str.secrets.get("GEMINI_API_KEY")

if not api_key:
    str.warning("Please configure your GEMINI_API_KEY in Streamlit Secrets.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Initialize chat history if it doesn't exist
    if "messages" not in str.session_state:
        str.session_state.messages = []

    # Display past chat messages
    for message in str.session_state.messages:
        with str.chat_message(message["role"]):
            str.markdown(message["content"])

    # React to user input
    if user_input := str.chat_input("Ask me anything..."):
        # Display user message
        with str.chat_message("user"):
            str.markdown(user_input)
        str.session_state.messages.append({"role": "user", "content": user_input})

        # Generate and display assistant response
        with str.chat_message("assistant"):
            with str.spinner("Thinking..."):
                try:
                    response = model.generate_content(user_input)
                    str.markdown(response.text)
                    str.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    str.error(f"Error: {e}")