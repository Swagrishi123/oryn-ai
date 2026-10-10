import streamlit as st
import math, re, urllib.parse, requests, io, sys
from pypdf import PdfReader
from groq import Groq
import sympy
from sympy import symbols, Symbol, Eq, solve, simplify, Rational

# --- Page Configuration ---
st.set_page_config(page_title="ORYN.AI", page_icon="✦", layout="centered")

# --- Custom Gemini Light UI Styling (Purple Text Edition) ---
st.markdown("""
<style>
    /* Force white background */
    .stApp {
        background-color: #ffffff !important;
        font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Fixed top header */
    .oryn-header {
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        padding: 12px 0 8px 0;
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
        text-align: center;
        margin-bottom: 20px;
    }
    .oryn-brand {
        display: inline-flex;
        align-items: center;
        gap: 10px;
    }
    .oryn-title {
        font-size: 2rem;
        font-weight: 700;
        color: #4a148c !important;
        margin: 0;
    }
    .oryn-subtitle {
        color: #7b1fa2 !important;
        font-size: 0.85rem;
        margin: 2px 0 0 0;
    }

    /* User Message Bubble */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background-color: #f3e8ff !important;
        border-radius: 18px !important;
        padding: 10px 16px !important;
        border: 1px solid #e9d5ff !important;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) * {
        color: #6b21a8 !important;
    }

    /* AI Assistant Message Bubble & Text */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #faf5ff !important;
        border-radius: 18px !important;
        padding: 12px 18px !important;
        border: 1px solid #f3e8ff !important;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) *,
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) p,
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) span {
        color: #4a148c !important;
        font-weight: 500;
    }

    /* Math, Formulas & Inline Code */
    code {
        background-color: #ede9fe !important;
        color: #581c87 !important;
        font-weight: 600 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header with Rosette Swirl Emblem ---
st.markdown("""
<div class="oryn-header">
    <div class="oryn-brand">
        <svg width="30" height="30" viewBox="0 0 24 24" fill="#4a148c" xmlns="http://www.w3.org/2000/svg">
            <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.771-4.2057 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7467-7.0731zM13.2599 22.4042a4.4568 4.4568 0 0 1-2.9001-1.0543l.1422-.0818 4.811-2.778a.791.791 0 0 0 .3955-.6855v-6.786l2.1643 1.25a.1582.1582 0 0 1 .0791.137v5.545a4.4628 4.4628 0 0 1-4.692 4.4536zM3.8205 18.0645a4.4568 4.4568 0 0 1-.5157-3.0568l.1422.0853 4.811 2.778a.791.791 0 0 0 .791 0l5.8753-3.3934v2.5a.1582.1582 0 0 1-.0791.137l-4.8 2.7717a4.4628 4.4628 0 0 1-6.2247-1.8218zm-1.8218-9.4264a4.4568 4.4568 0 0 1 2.3844-2.0025v5.7176a.791.791 0 0 0 .3955.6855l5.8753 3.3934-2.1643 1.25a.1582.1582 0 0 1-.1582 0l-4.8-2.7717a4.4628 4.4628 0 0 1-1.5327-6.2723zm13.931-1.0543-5.8753-3.3934 2.1643-1.25a.1582.1582 0 0 1 .1582 0l4.8 2.7717a4.4628 4.4628 0 0 1-.5157 8.5292v-5.972a.791.791 0 0 0-.7315-.6855zm3.8205 6.3686a4.4568 4.4568 0 0 1 .5157 3.0568l-.1422-.0853-4.811-2.778a.791.791 0 0 0-.791 0l-5.8753 3.3934v-2.5a.1582.1582 0 0 1 .0791-.137l4.8-2.7717a4.4628 4.4628 0 0 1 6.2247 1.8218zM10.7401 13.0847l-2.6105-1.507 2.6105-1.507 2.6105 1.507z"/>
        </svg>
        <h1 class="oryn-title">ORYN.AI</h1>
    </div>
    <p class="oryn-subtitle">Autonomous Intelligence • Grounded Reasoning • Precision Math</p>
</div>
""", unsafe_allow_html=True)

# --- API Key Setup & Model Discovery ---
raw_key = st.secrets.get("GROQ_API_KEY", None)
if not raw_key:
    with st.sidebar:
        st.subheader("Configuration")
        raw_key = st.text_input("Enter Groq API Key:", type="password")
        st.caption("Free key available at console.groq.com")

api_key = str(raw_key).strip() if raw_key else None
client = Groq(api_key=api_key) if api_key else None

active_model = "llama-3.1-8b-instant"
if client:
    try:
        available_models = [m.id for m in client.models.list().data]
        priority_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-3.2-3b-preview",
            "llama-3.2-1b-preview",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        for candidate in priority_models:
            if candidate in available_models:
                active_model = candidate
                break
        else:
            # Avoid whisper, vision, and guard models for chat
            valid_chat = [m for m in available_models if not any(x in m.lower() for x in ["whisper", "guard", "vision", "embed"])]
            if valid_chat:
                active_model = valid_chat[0]
    except Exception as err:
        st.sidebar.warning(f"Could not load models list: {err}")

with st.sidebar:
    st.caption(f"⚡ Active Engine: `{active_model}`")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- Helper Utilities ---
def execute_pure_math(expr: str) -> str:
    clean = expr.replace("x", "*").replace("X", "*").replace("^", "**").replace("÷", "/")
    safe_env = {"sin": math.sin, "cos": math.cos, "tan": math.tan, "sqrt": math.sqrt, "log": math.log, "factorial": math.factorial, "pi": math.pi, "e": math.e}
    try:
        return str(eval(clean, {"__builtins__": {}}, safe_env))
    except Exception as e:
        return f"Error: {e}"

def is_pure_math(text: str) -> bool:
    cleaned = re.sub(r"(?i)\b(sin|cos|tan|sqrt|log|exp|factorial|pi|e)\b", "", text.strip())
    if re.search(r"[a-zA-Z]", cleaned):
        return False
    return bool(re.search(r"\d", cleaned)) and any(op in cleaned for op in ["+", "-", "*", "/", "^", "%", "÷"])

def fetch_wiki(query: str) -> str:
    norm = re.sub(r"(?i)\bcm\b", "Chief Minister", query)
    norm = re.sub(r"(?i)\bpm\b", "Prime Minister", norm)
    norm = re.sub(r"(?i)\b(who is the|who is|what is the|what is|\?)\b", "", norm).strip()
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(norm)}&utf8=&format=json"
        res = requests.get(url, headers={"User-Agent": "ORYN/1.0 (contact: support@oryn.ai)"}, timeout=3).json()
        hits = res.get("query", {}).get("search", [])
        if hits:
            return f"[{hits[0].get('title')}]: " + re.sub(r"<[^>]+>", "", hits[0].get("snippet", ""))
    except Exception:
        pass
    return ""

def execute_code_solution(code_str: str) -> str:
    stdout_trap = io.StringIO()
    sys_stdout_backup = sys.stdout
    scope = {"math": math, "sympy": sympy, "symbols": symbols, "Symbol": Symbol, "Eq": Eq, "solve": solve, "simplify": simplify, "Rational": Rational, "pi": math.pi, "__builtins__": __builtins__}
    try:
        sys.stdout = stdout_trap
        exec("import math\nimport sympy\nfrom sympy import symbols, Eq, solve\n" + code_str, scope)
        return stdout_trap.getvalue().strip()
    except Exception as e:
        return f"EXEC_ERROR: {e}"
    finally:
        sys.stdout = sys_stdout_backup

# --- Chat Memory Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Document Attachment Drawer ---
with st.expander("📎 Attach Document (PDF)", expanded=False):
    uploaded_pdf = st.file_uploader("Upload PDF file", type=["pdf"], label_visibility="collapsed")
    pdf_text = ""
    if uploaded_pdf:
        reader = PdfReader(uploaded_pdf)
        pdf_text = "".join([p.extract_text() or "" for p in reader.pages[:8]])[:3500]
        st.success(f"Attached: {uploaded_pdf.name}")

# --- Render Chat History ---
for msg in st.session_state.messages:
    if msg.get("content"):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- User Input & Router ---
user_input = st.chat_input("Ask ORYN...")

if user_input:
    # 1. Render user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = ""
    t_lower = user_input.lower()

    # 2. Build history excluding current input to prevent duplicate user turns
    history = []
    for m in st.session_state.messages[:-1]:
        if m.get("content"):
            history.append({"role": m["role"], "content": m["content"]})
    history = history[-4:]

    with st.chat_message("assistant"):
        with st.spinner("ORYN is thinking..."):
            if not client:
                response = "Please enter a valid Groq API key to activate ORYN.AI."
            elif pdf_text:
                prompt = f"Document Excerpt:\n{pdf_text}\n\nQuestion: {user_input}\nAnswer clearly based on the document."
                try:
                    res = client.chat.completions.create(model=active_model, messages=[{"role": "user", "content": prompt}], max_tokens=600)
                    msg_obj = res.choices[0].message
                    response = msg_obj.content or getattr(msg_obj, "reasoning", "") or "No text generated."
                except Exception as err:
                    response = f"Groq Error: {err}"
            elif is_pure_math(user_input):
                response = f"`{user_input} = {execute_pure_math(user_input)}`"
            elif any(sig in t_lower for sig in ["speed", "distance", "ratio", "compounded", "compound interest", "profit", "loss", "discount", "upstream", "downstream", "work in"]):
                code_prompt = f"Write ONLY a Python script inside ```python ... ``` that prints a step-by-step solution and final answer for: {user_input}"
                try:
                    code_res = client.chat.completions.create(model=active_model, messages=[{"role": "user", "content": code_prompt}], max_tokens=650)
                    raw_code = code_res.choices[0].message.content or ""
                    match = re.search(r"```(?:python)?\s*(.*?)\s*```", raw_code, re.DOTALL)
                    if match:
                        exec_out = execute_code_solution(match.group(1))
                        response = exec_out if exec_out and not exec_out.startswith("EXEC_ERROR:") else raw_code
                    else:
                        response = raw_code
                except Exception as err:
                    response = f"Groq Error: {err}"
            else:
                wiki_ctx = fetch_wiki(user_input)
                sys_msg = "You are ORYN.AI. Answer naturally in 2-3 sentences."
                user_msg = f"Context: {wiki_ctx}\n\nQuestion: {user_input}" if wiki_ctx else user_input
                conv = [{"role": "system", "content": sys_msg}] + history + [{"role": "user", "content": user_msg}]
                try:
                    res = client.chat.completions.create(model=active_model, messages=conv, max_tokens=600)
                    msg_obj = res.choices[0].message
                    response = msg_obj.content or getattr(msg_obj, "reasoning", "") or "No answer returned."
                except Exception as err:
                    response = f"Groq Error: {err}"

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
