# 🤖 Personal GPT Bot (Python)

A Python-based personal GPT chatbot powered by the OpenAI API. It includes:
1. **CLI Terminal Bot (`bot.py`)**: Real-time streaming responses, conversation history memory, model switching, and slash commands.
2. **Web Browser UI (`app.py`)**: A modern ChatGPT-like web interface powered by FastAPI & Vercel serverless with custom temperature, model switching, and chat management.

---

## 🚀 Quick Start

### 1. Set your OpenAI API Key
Open the `.env` file in this directory and paste your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

---

### 2. Run Locally

#### Option A: Web App (FastAPI - Vercel Ready)
Run the web application locally:
```bash
python app.py
```
Or with uvicorn:
```bash
uvicorn app:app --reload
```
Open `http://localhost:8000` in your browser.

#### Option B: Terminal Chatbot (CLI)
```bash
python bot.py
```

---

## ☁️ Deploy to Vercel

1. Commit and push your code to your GitHub repository:
   ```bash
   git add .
   git commit -m "Configure FastAPI entrypoint for Vercel deployment"
   git push
   ```
2. In your **Vercel Dashboard**:
   - Go to your Project Settings -> **Environment Variables**.
   - Add `OPENAI_API_KEY` with your OpenAI API key value.
3. Redeploy the project on Vercel. Vercel will automatically discover the `app` export in `app.py`.

---

## 📁 Project Structure

```
chatboat/
├── bot.py             # Terminal/CLI chatbot with streaming & memory
├── app.py             # FastAPI browser-based chatbot UI (Vercel-ready)
├── vercel.json        # Vercel deployment and routing configuration
├── requirements.txt   # Dependencies (fastapi, uvicorn, openai, pydantic, python-dotenv)
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
