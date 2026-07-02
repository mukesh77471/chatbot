import streamlit as st
import google.generativeai as genai
import requests

# Configure the page
st.set_page_config(page_title="Free Chatbot", page_icon="🤖")
st.title("🤖 Mukesh AI Assistant – For All Your Queries")

# Securely fetch the API key (Streamlit Secrets handles this in deployment)
api_key = st.secrets.get("GEMINI_API_KEY")
bing_key = st.secrets.get("BING_API_KEY")

if not api_key:
    st.warning("Please configure your GEMINI_API_KEY in Streamlit Secrets.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.5-flash")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display past chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if user_input := st.chat_input("Ask me anything..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Step 1: Web search for every query
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

                    # Step 2: Combine user input + web search results
                    prompt = f"User asked: {user_input}\n\nLatest web search results:\n{web_data}\n\nAnswer clearly in Hindi with references."

                    # Step 3: Gemini response
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")
