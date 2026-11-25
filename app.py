"""
Streamlit Web UI for your Personal GPT Chatbot
"""

import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="My Personal GPT Bot",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 My Personal GPT Bot")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    env_api_key = os.getenv("OPENAI_API_KEY", "")
    api_key_input = st.text_input(
        "OpenAI API Key",
        value=env_api_key,
        type="password",
        help="Enter your OpenAI API key (starts with sk-...)",
    )

    model_options = [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ]

    selected_model = st.selectbox(
        "Choose Model",
        options=model_options,
        index=0,
    )

    custom_model = st.text_input("Or custom model name (optional)", "")
    active_model = custom_model.strip() if custom_model.strip() else selected_model

    temperature = st.slider("Temperature (Creativity)", 0.0, 2.0, 0.7, 0.1)

    system_prompt = st.text_area(
        "System Instructions / Persona",
        value="You are a helpful, knowledgeable, and friendly AI assistant.",
        height=100,
    )

    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("💡 **Tip**: Add your key to `.env` so you don't have to enter it each time.")

# Check API Key
if not api_key_input:
    st.info("👋 Please enter your OpenAI API key in the sidebar to start chatting.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=api_key_input)

# Initialize chat messages in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User prompt input
if prompt := st.chat_input("Ask me anything..."):
    # Append and render user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build full message payload including system prompt
    payload = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages:
        payload.append({"role": msg["role"], "content": msg["content"]})

    # Render assistant streaming response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model=active_model,
                messages=payload,
                temperature=temperature,
                stream=True,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_response += delta
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except AuthenticationError:
            st.error("Authentication failed. Please verify your OpenAI API key.")
        except RateLimitError as e:
            st.error(f"Rate limit or quota reached: {e}")
        except APIConnectionError:
            st.error("Connection error. Could not connect to OpenAI API.")
        except Exception as e:
            st.error(f"Error: {e}")
