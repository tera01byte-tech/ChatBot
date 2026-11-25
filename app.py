import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError

# Load environment variables
load_dotenv()

# Top-level ASGI entrypoint required by Vercel
app = FastAPI(title="ChatBot")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "gpt-4o-mini"
    system_prompt: Optional[str] = "You are a helpful, knowledgeable, and friendly AI assistant."
    api_key: Optional[str] = None


HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ChatBot</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root {
      --bg: #0f172a;
      --sidebar: #1e293b;
      --chat-bg: #0f172a;
      --card-bg: #1e293b;
      --user-msg: #3b82f6;
      --bot-msg: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --border: #334155;
      --accent: #2563eb;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      display: flex;
      height: 100vh;
      overflow: hidden;
    }
    /* Sidebar */
    #sidebar {
      width: 290px;
      background: var(--sidebar);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      padding: 20px;
      gap: 16px;
    }
    #sidebar h2 { font-size: 1.2rem; display: flex; align-items: center; gap: 8px; }
    .setting-group { display: flex; flex-direction: column; gap: 6px; }
    .setting-group label { font-size: 0.8rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
    input, select, textarea {
      width: 100%;
      padding: 10px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: #0f172a;
      color: var(--text);
      font-size: 0.9rem;
      outline: none;
    }
    input:focus, select:focus, textarea:focus { border-color: var(--accent); }
    textarea { resize: vertical; min-height: 70px; font-family: inherit; }
    button {
      padding: 10px 14px;
      border-radius: 8px;
      border: none;
      background: var(--accent);
      color: white;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
    }
    button:hover { background: #1d4ed8; }
    button.btn-secondary {
      background: #475569;
    }
    button.btn-secondary:hover { background: #64748b; }
    
    /* Main Chat Area */
    #chat-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      background: var(--chat-bg);
      height: 100%;
    }
    #chat-header {
      padding: 16px 24px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--sidebar);
    }
    #chat-header h1 { font-size: 1.25rem; font-weight: 700; display: flex; align-items: center; gap: 8px; }
    #messages {
      flex: 1;
      overflow-y: auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }
    .message {
      max-width: 80%;
      padding: 14px 18px;
      border-radius: 12px;
      line-height: 1.5;
      font-size: 0.95rem;
      word-wrap: break-word;
    }
    .message.user {
      align-self: flex-end;
      background: var(--user-msg);
      color: white;
      border-bottom-right-radius: 4px;
    }
    .message.bot {
      align-self: flex-start;
      background: var(--bot-msg);
      color: var(--text);
      border-bottom-left-radius: 4px;
    }
    .message pre {
      background: #090d16;
      padding: 10px;
      border-radius: 6px;
      overflow-x: auto;
      margin-top: 8px;
    }
    .message code { font-family: monospace; font-size: 0.9em; }
    
    /* Input Form */
    #input-form {
      padding: 16px 24px;
      border-top: 1px solid var(--border);
      display: flex;
      gap: 12px;
      background: var(--sidebar);
    }
    #user-prompt {
      flex: 1;
      padding: 12px 16px;
      font-size: 0.95rem;
      border-radius: 10px;
    }
    #send-btn { min-width: 90px; }
    
    @media (max-width: 768px) {
      body { flex-direction: column; }
      #sidebar { width: 100%; height: auto; padding: 12px; }
      .message { max-width: 95%; }
    }
  </style>
</head>
<body>
  <div id="sidebar">
    <h2>🤖 ChatBot</h2>
    
    <div class="setting-group">
      <label for="api-key">OpenAI API Key (Optional)</label>
      <input type="password" id="api-key" placeholder="Uses server key if empty">
    </div>

    <div class="setting-group">
      <label for="model">Model</label>
      <select id="model">
        <option value="gpt-4o-mini" selected>gpt-4o-mini (Fast & Cost Efficient)</option>
        <option value="gpt-4o">gpt-4o (Most Intelligent)</option>
        <option value="gpt-4-turbo">gpt-4-turbo</option>
        <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
      </select>
    </div>

    <div class="setting-group">
      <label for="system-prompt">System Prompt</label>
      <textarea id="system-prompt">You are a helpful, knowledgeable, and friendly AI assistant.</textarea>
    </div>

    <button class="btn-secondary" onclick="clearChat()">🧹 Clear Conversation</button>
  </div>

  <div id="chat-container">
    <div id="chat-header">
      <h1>🤖 ChatBot</h1>
      <span style="font-size: 0.85rem; color: #22c55e; display: flex; align-items: center; gap: 6px;" id="status">
        <span style="display:inline-block; width:8px; height:8px; background:#22c55e; border-radius:50%;"></span> Online
      </span>
    </div>

    <div id="messages">
      <div class="message bot">
        Hello! I am <strong>ChatBot</strong>, your personal AI assistant. How can I help you today?
      </div>
    </div>

    <form id="input-form" onsubmit="sendMessage(event)">
      <input type="text" id="user-prompt" placeholder="Type your message..." autocomplete="off" required>
      <button type="submit" id="send-btn">Send</button>
    </form>
  </div>

  <script>
    let conversationHistory = [];

    function clearChat() {
      conversationHistory = [];
      document.getElementById('messages').innerHTML = `
        <div class="message bot">Conversation cleared. What would you like to talk about next?</div>
      `;
    }

    async function sendMessage(e) {
      e.preventDefault();
      const promptInput = document.getElementById('user-prompt');
      const text = promptInput.value.trim();
      if (!text) return;

      const apiKey = document.getElementById('api-key').value.trim();
      const model = document.getElementById('model').value;
      const systemPrompt = document.getElementById('system-prompt').value.trim();
      const messagesContainer = document.getElementById('messages');
      const sendBtn = document.getElementById('send-btn');

      // Append user message to UI
      const userDiv = document.createElement('div');
      userDiv.className = 'message user';
      userDiv.innerText = text;
      messagesContainer.appendChild(userDiv);
      promptInput.value = '';
      messagesContainer.scrollTop = messagesContainer.scrollHeight;

      // Update internal history
      conversationHistory.push({ role: 'user', content: text });

      // Create placeholder for bot reply
      const botDiv = document.createElement('div');
      botDiv.className = 'message bot';
      botDiv.innerHTML = '<span style="color:var(--text-muted)">Thinking...</span>';
      messagesContainer.appendChild(botDiv);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;

      sendBtn.disabled = true;
      let fullReply = '';

      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            messages: conversationHistory,
            model: model,
            system_prompt: systemPrompt,
            api_key: apiKey || null
          })
        });

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || 'Failed to get response');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        botDiv.innerHTML = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          fullReply += chunk;
          botDiv.innerHTML = marked.parse(fullReply);
          messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        conversationHistory.push({ role: 'assistant', content: fullReply });
      } catch (err) {
        botDiv.innerHTML = `<span style="color:#ef4444;">⚠️ Error: ${err.message}</span>`;
      } finally {
        sendBtn.disabled = false;
        promptInput.focus();
      }
    }
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serves the ChatGPT Web UI."""
    return HTML_CONTENT


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Processes chat messages and streams the GPT response."""
    # Resolve API Key: client provided or server environment variable
    api_key = request.api_key or os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API Key is missing. Please set OPENAI_API_KEY in environment variables or enter it in the sidebar."
        )

    client = OpenAI(api_key=api_key)

    # Build messages with system prompt
    messages = [{"role": "system", "content": request.system_prompt}]
    for msg in request.messages:
        messages.append({"role": msg.role, "content": msg.content})

    def stream_generator():
        try:
            stream = client.chat.completions.create(
                model=request.model or "gpt-4o-mini",
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield delta
        except AuthenticationError:
            yield "❌ Authentication Error: Invalid OpenAI API Key."
        except RateLimitError as e:
            yield f"⚠️ Rate Limit Error: {str(e)}"
        except APIConnectionError:
            yield "❌ Network Error: Could not connect to OpenAI."
        except Exception as e:
            yield f"❌ Error: {str(e)}"

    return StreamingResponse(stream_generator(), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
