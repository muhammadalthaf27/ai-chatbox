"""
AI Chatbot Assistant — Muhammad Althaf S
=========================================
Stack : Python 3.9+, Flask, Google Gemini API
Run   : pip install flask google-generativeai
        python app.py
Then open: http://localhost:5000

Get free Gemini API key: https://aistudio.google.com/app/apikey
Replace YOUR_GEMINI_API_KEY below with your key.
"""

from flask import Flask, render_template_string, request, jsonify, session
import google.generativeai as genai
import os, uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ─── CONFIG ───────────────────────────────────────────────────────────────────
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"   # ← replace this
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """You are Althaf's AI Assistant — a helpful, friendly, and concise chatbot 
built by Muhammad Althaf S. You help users with general questions, coding problems, 
career advice, and technical topics. Be conversational, clear, and professional.
Keep answers focused and readable. Use markdown for code blocks."""

# ─── HTML TEMPLATE (full single-file app) ────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AI Chatbot — Muhammad Althaf</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0d0d14;--card:#16161f;--border:#ffffff10;--accent:#4f8ef7;--accent2:#7c5cfc;--green:#22d3a0;--text:#f0f0f8;--muted:#888899;--user-bg:linear-gradient(135deg,#4f8ef7,#7c5cfc);--bot-bg:#1e1e2a}
body{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;height:100vh;display:flex;flex-direction:column;overflow:hidden}
/* HEADER */
header{padding:1rem 1.5rem;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:1rem;background:#0d0d14ee;backdrop-filter:blur(20px);flex-shrink:0}
.bot-avatar{width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0}
.bot-info h1{font-family:'Syne',sans-serif;font-size:1rem;font-weight:700}
.bot-status{font-size:.75rem;color:var(--green);display:flex;align-items:center;gap:.3rem}
.dot{width:6px;height:6px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.clear-btn{margin-left:auto;background:transparent;border:1px solid var(--border);color:var(--muted);padding:.4rem .9rem;border-radius:8px;font-size:.78rem;cursor:pointer;font-family:'DM Sans',sans-serif;transition:all .2s}
.clear-btn:hover{border-color:var(--accent);color:var(--accent)}
/* CHAT AREA */
#chat{flex:1;overflow-y:auto;padding:1.5rem;display:flex;flex-direction:column;gap:1rem;scroll-behavior:smooth}
#chat::-webkit-scrollbar{width:4px}
#chat::-webkit-scrollbar-track{background:transparent}
#chat::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
.msg{display:flex;gap:.8rem;max-width:82%;animation:slideIn .3s ease}
@keyframes slideIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.msg.user{align-self:flex-end;flex-direction:row-reverse}
.msg-avatar{width:32px;height:32px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:.85rem;flex-shrink:0;margin-top:.2rem}
.msg.bot .msg-avatar{background:linear-gradient(135deg,var(--accent),var(--accent2))}
.msg.user .msg-avatar{background:#ffffff15;border:1px solid var(--border)}
.msg-bubble{padding:.85rem 1.1rem;border-radius:16px;line-height:1.65;font-size:.92rem;font-weight:300}
.msg.bot .msg-bubble{background:var(--bot-bg);border:1px solid var(--border);border-top-left-radius:4px}
.msg.user .msg-bubble{background:var(--user-bg);color:#fff;border-top-right-radius:4px}
.msg-bubble pre{background:#0a0a0f;border:1px solid var(--border);border-radius:8px;padding:.8rem;margin:.6rem 0;overflow-x:auto;font-size:.82rem}
.msg-bubble code{font-family:'Courier New',monospace;background:#0a0a0f;padding:.1rem .3rem;border-radius:4px;font-size:.85rem}
.msg-bubble pre code{background:transparent;padding:0}
/* TYPING */
.typing-indicator{display:flex;gap:.4rem;padding:.9rem 1.1rem;background:var(--bot-bg);border:1px solid var(--border);border-radius:16px;border-top-left-radius:4px;width:fit-content}
.typing-indicator span{width:6px;height:6px;border-radius:50%;background:var(--muted);animation:bounce .9s infinite}
.typing-indicator span:nth-child(2){animation-delay:.15s}
.typing-indicator span:nth-child(3){animation-delay:.3s}
@keyframes bounce{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-6px)}}
/* SUGGESTIONS */
.suggestions{display:flex;gap:.5rem;flex-wrap:wrap;padding:0 1.5rem .8rem}
.suggestion{background:#ffffff06;border:1px solid var(--border);color:var(--muted);padding:.4rem .85rem;border-radius:8px;font-size:.78rem;cursor:pointer;transition:all .2s;font-family:'DM Sans',sans-serif}
.suggestion:hover{border-color:var(--accent);color:var(--accent)}
/* INPUT */
.input-area{padding:1rem 1.5rem 1.5rem;border-top:1px solid var(--border);flex-shrink:0}
.input-wrap{display:flex;gap:.8rem;background:var(--card);border:1px solid var(--border);border-radius:14px;padding:.5rem .5rem .5rem 1rem;transition:border-color .2s}
.input-wrap:focus-within{border-color:#4f8ef760}
#userInput{flex:1;background:transparent;border:none;outline:none;color:var(--text);font-size:.93rem;font-family:'DM Sans',sans-serif;font-weight:400;resize:none;max-height:120px;line-height:1.5;padding:.3rem 0}
#userInput::placeholder{color:var(--muted)}
#sendBtn{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,var(--accent),var(--accent2));border:none;color:#fff;font-size:1.1rem;cursor:pointer;flex-shrink:0;transition:opacity .2s;display:flex;align-items:center;justify-content:center}
#sendBtn:hover{opacity:.85}
#sendBtn:disabled{opacity:.4;cursor:not-allowed}
.input-hint{font-size:.72rem;color:var(--muted);margin-top:.5rem;text-align:center}
</style>
</head>
<body>
<header>
  <div class="bot-avatar">🤖</div>
  <div class="bot-info">
    <h1>Althaf's AI Assistant</h1>
    <div class="bot-status"><span class="dot"></span> Online · Powered by Gemini</div>
  </div>
  <button class="clear-btn" onclick="clearChat()">Clear chat</button>
</header>

<div id="chat">
  <div class="msg bot">
    <div class="msg-avatar">🤖</div>
    <div class="msg-bubble">
      Hey! 👋 I'm <strong>Althaf's AI Assistant</strong>, built by Muhammad Althaf S using the Gemini API.<br/><br/>
      I can help you with <strong>coding questions</strong>, <strong>career advice</strong>, <strong>technical topics</strong>, or just a friendly chat. What's on your mind?
    </div>
  </div>
</div>

<div class="suggestions" id="suggestions">
  <button class="suggestion" onclick="suggest(this)">Who is Muhammad Althaf?</button>
  <button class="suggestion" onclick="suggest(this)">Explain Python in simple terms</button>
  <button class="suggestion" onclick="suggest(this)">Tips to crack a tech interview</button>
  <button class="suggestion" onclick="suggest(this)">What is machine learning?</button>
</div>

<div class="input-area">
  <div class="input-wrap">
    <textarea id="userInput" placeholder="Ask me anything..." rows="1"></textarea>
    <button id="sendBtn" onclick="sendMessage()">➤</button>
  </div>
  <div class="input-hint">Press Enter to send · Shift+Enter for new line</div>
</div>

<script>
let history = [];

function escapeHtml(text) {
  return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function formatMessage(text) {
  // code blocks
  text = text.replace(/```(\w*)\n?([\s\S]*?)```/g, (_,lang,code) =>
    `<pre><code>${escapeHtml(code.trim())}</code></pre>`);
  // inline code
  text = text.replace(/`([^`]+)`/g, (_,c) => `<code>${escapeHtml(c)}</code>`);
  // bold
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // newlines
  text = text.replace(/\n/g, '<br/>');
  return text;
}

function addMessage(role, content) {
  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  const avatar = role === 'bot' ? '🤖' : '👤';
  div.innerHTML = `<div class="msg-avatar">${avatar}</div><div class="msg-bubble">${formatMessage(content)}</div>`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

function showTyping() {
  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = 'msg bot';
  div.id = 'typing';
  div.innerHTML = `<div class="msg-avatar">🤖</div><div class="typing-indicator"><span></span><span></span><span></span></div>`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function hideTyping() {
  const el = document.getElementById('typing');
  if (el) el.remove();
}

function suggest(btn) {
  document.getElementById('userInput').value = btn.textContent;
  document.getElementById('suggestions').style.display = 'none';
  sendMessage();
}

function clearChat() {
  history = [];
  const chat = document.getElementById('chat');
  chat.innerHTML = `<div class="msg bot"><div class="msg-avatar">🤖</div><div class="msg-bubble">Chat cleared! How can I help you? 😊</div></div>`;
  document.getElementById('suggestions').style.display = 'flex';
}

async function sendMessage() {
  const input = document.getElementById('userInput');
  const btn = document.getElementById('sendBtn');
  const text = input.value.trim();
  if (!text) return;

  document.getElementById('suggestions').style.display = 'none';
  input.value = '';
  input.style.height = 'auto';
  btn.disabled = true;

  addMessage('user', text);
  history.push({ role: 'user', content: text });
  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, history })
    });
    const data = await res.json();
    hideTyping();
    if (data.reply) {
      addMessage('bot', data.reply);
      history.push({ role: 'assistant', content: data.reply });
    } else {
      addMessage('bot', '⚠️ Sorry, something went wrong. Please try again.');
    }
  } catch {
    hideTyping();
    addMessage('bot', '⚠️ Network error. Make sure the server is running.');
  }
  btn.disabled = false;
  input.focus();
}

// Enter to send
document.getElementById('userInput').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  // auto-resize
  setTimeout(() => {
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
  }, 0);
});
</script>
</body>
</html>"""

# ─── ROUTES ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data    = request.get_json()
    message = data.get("message", "")
    history = data.get("history", [])

    # Build conversation for Gemini
    chat_history = []
    for h in history[:-1]:   # exclude current message (already in history)
        role    = "user" if h["role"] == "user" else "model"
        chat_history.append({"role": role, "parts": [h["content"]]})

    try:
        conversation = model.start_chat(history=chat_history)
        full_prompt  = f"{SYSTEM_PROMPT}\n\nUser: {message}" if not chat_history else message
        response     = conversation.send_message(full_prompt)
        reply        = response.text
    except Exception as e:
        reply = f"⚠️ Error: {str(e)}\n\nMake sure your Gemini API key is set correctly in app.py"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    print("\n🤖 Althaf's AI Chatbot is running!")
    print("👉 Open: http://localhost:5000")
    print("🔑 Remember to add your Gemini API key in app.py\n")
    app.run(debug=True, port=5000)
