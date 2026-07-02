import streamlit as st
from google import genai
from google.genai.errors import APIError
import requests

# Configure the page
st.set_page_config(page_title="Free Chatbot", page_icon="🤖")
st.title("🤖 Mukesh AI Assistant – For All Your Queries")

# Securely fetch API keys
api_key = st.secrets.get("GEMINI_API_KEY")
bing_key = st.secrets.get("BING_API_KEY")

if not api_key:
    st.warning("Please configure your GEMINI_API_KEY in Streamlit Secrets.")
else:
    # Initialize the modern Google GenAI Client
    client = genai.Client(api_key=api_key)
    
    # Swapped to standard 'gemini-2.5-flash' for significantly higher daily free tier caps
    MODEL_NAME = "gemini-2.5-flash"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display past chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input (Placed inside the authenticated block)
    if user_input := st.chat_input("Ask me anything..."):
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        # Save user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Step 1: Web search
        search_url = f"https://api.bing.microsoft.com/v7.0/search?q={user_input}"
        headers = {"Ocp-Apim-Subscription-Key": bing_key}
        web_data = ""
        try:
            resp = requests.get(search_url, headers=headers)
            if resp.status_code == 200:
                results = resp.json()
                if "webPages" in results:
                    snippets = [
                        f"{item['name']}: {item['snippet']} ({item['url']})"
                        for item in results["webPages"]["value"][:3]
                    ]
                    web_data = "\n".join(snippets)
        except Exception as e:
            web_data = f"(Web search error: {e})"

        # Step 2: Build conversation context (last 5 turns)
        history_text = ""
        for msg in st.session_state.messages[-5:]:
            history_text += f"{msg['role'].capitalize()}: {msg['content']}\n"

        # Step 3: Prompt framework
        prompt = f"""Conversation so far:
{history_text}

Web search results:
{web_data}

Answer naturally in the same language the user typed, continue the conversation like a human assistant, and include references when useful."""

        # Step 4: Gemini response generation
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Utilizing the modern SDK generation call
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt,
                    )
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except APIError as api_err:
                    if api_err.code == 429:
                        st.error("Rate limit reached. Please wait a moment before sending another message.")
                    else:
                        st.error(f"Gemini API Error: {api_err.message}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")