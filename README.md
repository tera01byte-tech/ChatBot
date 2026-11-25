# 🤖 Personal GPT Bot (Python)

A Python-based personal GPT chatbot powered by the OpenAI API. It includes:
1. **CLI Terminal Bot (`bot.py`)**: Real-time streaming responses, conversation history memory, model switching, and slash commands.
2. **Web Browser UI (`app.py`)**: A modern ChatGPT-like web interface powered by Streamlit with custom temperature, model switching, and chat management.

---

## 🚀 Quick Start

### 1. Set your OpenAI API Key
Open the `.env` file in this directory and paste your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

*(If you don't enter it into `.env`, the bot will ask you for it when you run it).*

---

### 2. Activate Virtual Environment
The virtual environment is already prepared in `venv/`. Activate it with:

```bash
source venv/bin/activate
```

---

### 3. Run the Chatbot

#### Option A: Terminal Chatbot (CLI)
Run the interactive terminal bot:
```bash
python bot.py
```

**Commands inside the CLI bot:**
- `/clear` - Reset conversation memory
- `/model <name>` - Switch model (e.g., `/model gpt-4o`, `/model gpt-4o-mini`)
- `/system <text>` - Change the bot's persona/system prompt
- `/history` - View number of messages in the current session
- `/exit` or `exit` - Quit

#### Option B: Web Chatbot (Streamlit UI)
Run the web application:
```bash
streamlit run app.py
```
This will automatically open your web browser with a full chat interface at `http://localhost:8501`.

---

## 📁 Project Structure

```
chatboat/
├── bot.py             # Terminal/CLI chatbot with streaming & memory
├── app.py             # Streamlit browser-based chatbot UI
├── requirements.txt   # Dependencies (openai, streamlit, python-dotenv)
├── .env               # Your private API key and configurations (ignored by git)
├── .env.example       # Example configuration template
├── .gitignore         # Prevents committing .env or venv
└── README.md          # Project documentation
```

---

## ⚙️ Supported Models
You can use any OpenAI chat completion model, such as:
- `gpt-4o-mini` *(Recommended: fast, cost-efficient, highly intelligent)*
- `gpt-4o` *(Flagship model for complex tasks)*
- `gpt-4-turbo`
- `gpt-3.5-turbo`
