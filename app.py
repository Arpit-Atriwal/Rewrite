import streamlit as st
from google import genai
from google.genai import types

# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Rewrite with Copilot",
    layout="centered",
    page_icon="✨",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# Design system — matching the Edge "Rewrite with Copilot"
# floating card: rounded pill chips, blue→purple gradient
# accent, soft elevation, Segoe-first type stack.
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --grad: linear-gradient(135deg, #0D6EFD 0%, #7C3AED 55%, #06B6D4 100%);
        --ink: #1B1B1F;
        --ink-soft: #5B5B65;
        --surface: #FFFFFF;
        --page: #F3F3F5;
        --border: #E4E4E9;
        --border-hover: #C9C9F5;
    }

    html, body, [class*="css"] {
        font-family: 'Segoe UI Variable Text', 'Segoe UI', Inter, system-ui, sans-serif;
    }

    .stApp { background: var(--page); }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2.5rem; max-width: 640px; }

    /* ---------- Floating card ---------- */
    .cop-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 22px 24px 20px 24px;
        box-shadow: 0 8px 30px rgba(20,20,40,0.08), 0 1px 2px rgba(20,20,40,0.04);
        margin-bottom: 16px;
        animation: cop-in 0.35s ease-out;
    }
    @keyframes cop-in {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ---------- Header ---------- */
    .cop-header { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
    .cop-orb {
        width: 30px; height: 30px; border-radius: 50%;
        background: var(--grad);
        flex-shrink: 0;
        box-shadow: 0 0 0 4px rgba(124,58,237,0.08);
    }
    .cop-title { font-weight: 600; font-size: 1.05rem; color: var(--ink); line-height: 1.2; }
    .cop-subtitle { font-size: 0.82rem; color: var(--ink-soft); margin-top: 1px; }

    /* ---------- Section labels ---------- */
    .cop-label {
        font-size: 0.78rem; font-weight: 600; color: var(--ink-soft);
        margin: 14px 0 6px 0;
    }

    /* ---------- Text area (this IS the rewrite surface) ---------- */
    .stTextArea textarea {
        font-family: 'Segoe UI Variable Text', 'Segoe UI', Inter, sans-serif !important;
        font-size: 14.5px !important;
        line-height: 1.5 !important;
        border-radius: 12px !important;
        background: #FAFAFC !important;
        color: var(--ink) !important;
        border: 1px solid var(--border) !important;
        transition: border-color 0.15s ease, background 0.2s ease;
    }
    .stTextArea textarea:focus {
        border: 1px solid #7C3AED !important;
        box-shadow: 0 0 0 3px rgba(124,58,237,0.12) !important;
    }

    /* ---------- Pills (tone / length selectors) ---------- */
    div[data-testid="stPills"] label {
        border-radius: 999px !important;
        border: 1px solid var(--border) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 5px 14px !important;
        transition: all 0.15s ease !important;
        background: #FAFAFC !important;
    }
    div[data-testid="stPills"] label:hover {
        border-color: var(--border-hover) !important;
        transform: translateY(-1px);
    }
    div[data-testid="stPills"] label[data-checked="true"] {
        background: var(--grad) !important;
        border-color: transparent !important;
        color: white !important;
    }

    /* ---------- Buttons ---------- */
    div.stButton > button[kind="primary"] {
        background: var(--grad) !important;
        border: none !important;
        border-radius: 999px !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.5rem 1.2rem !important;
        box-shadow: 0 4px 14px rgba(124,58,237,0.28);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(124,58,237,0.38);
    }
    div.stButton > button[kind="secondary"] {
        background: #FAFAFC !important;
        border: 1px solid var(--border) !important;
        border-radius: 999px !important;
        color: var(--ink) !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        transition: all 0.15s ease;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: var(--border-hover) !important;
        background: #F5F3FF !important;
    }
    div.stButton > button:disabled {
        opacity: 0.4 !important;
    }

    /* ---------- Notices ---------- */
    div[data-testid="stNotification"] {
        border-radius: 12px !important;
    }

    /* ---------- Loading shimmer text ---------- */
    .cop-loading {
        font-size: 0.85rem; font-weight: 500;
        background: var(--grad);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: cop-shimmer 1.4s linear infinite;
    }
    @keyframes cop-shimmer {
        0% { background-position: 0% center; }
        100% { background-position: 200% center; }
    }

    /* ---------- Rewritten badge ---------- */
    .cop-badge {
        display: inline-block;
        font-size: 0.72rem; font-weight: 600;
        color: #7C3AED;
        background: #F5F3FF;
        border: 1px solid #E6E1FA;
        border-radius: 999px;
        padding: 2px 10px;
        margin-bottom: 8px;
        animation: cop-in 0.3s ease-out;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session state — the text box is rewritten in place.
# `version` bumps whenever we programmatically overwrite the
# textarea's content (Streamlit needs a fresh widget key to
# accept a new default value for an already-rendered widget).
# ---------------------------------------------------------
if "cop_version" not in st.session_state:
    st.session_state.cop_version = 0
if "cop_text" not in st.session_state:
    st.session_state.cop_text = ""
if "cop_original" not in st.session_state:
    st.session_state.cop_original = None   # baseline text, set on first rewrite
if "cop_rewritten" not in st.session_state:
    st.session_state.cop_rewritten = False

# ---------------------------------------------------------
# Card: header
# ---------------------------------------------------------
# st.markdown("""
#     <div class="cop-card">
#         <div class="cop-header">
           
#         </div>
#     </div>
# """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Card: input + controls
# ---------------------------------------------------------
#st.markdown('<div class="cop-card">', unsafe_allow_html=True)

st.markdown('<div class="cop-label">Your text</div>', unsafe_allow_html=True)

if st.session_state.cop_rewritten:
    st.markdown('<span class="cop-badge">✓ Rewritten</span>', unsafe_allow_html=True)

editor_key = f"cop_editor_{st.session_state.cop_version}"
current_text = st.text_area(
    "Your text:", height=160,
    value=st.session_state.cop_text,
    placeholder="Paste or type the text you want rewritten...",
    label_visibility="collapsed",
    key=editor_key
)

st.markdown('<div class="cop-label">Tone</div>', unsafe_allow_html=True)
tone = st.pills(
    "Tone", ["Professional", "Casual", "Enthusiastic", "Informational", "Formal", "Funny", "In Bullet Points"],
    default="Professional", label_visibility="collapsed"
)

st.markdown('<div class="cop-label">Length</div>', unsafe_allow_html=True)
length = st.pills(
    "Length", ["Shorter", "Same length", "Longer"],
    default="Same length", label_visibility="collapsed"
)

extra_instructions = st.text_input(
    "Custom instructions (optional)",
    placeholder="Any other instructions? e.g. keep it under 3 sentences",
    label_visibility="collapsed"
)

col_a, col_b, col_c = st.columns([1.3, 1, 1])
with col_a:
    rewrite_button = st.button("✨ Rewrite", type="primary", use_container_width=True)
with col_b:
    regenerate_button = st.button(
        "↻ Regenerate", type="secondary", use_container_width=True,
        disabled=not st.session_state.cop_rewritten
    )
with col_c:
    undo_button = st.button(
        "Undo", type="secondary", use_container_width=True,
        disabled=not st.session_state.cop_rewritten
    )

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Actions
# ---------------------------------------------------------
def do_rewrite(source_text: str):
    if not source_text.strip():
        st.warning("Add some text before asking Copilot to rewrite it.")
        return

    placeholder = st.empty()
    placeholder.markdown('<div class="cop-loading">Writing your text...</div>', unsafe_allow_html=True)

    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=gemini_key)

        length_hint = {
            "Shorter": "Make the rewrite noticeably shorter than the original.",
            "Longer": "Make the rewrite noticeably longer and more detailed than the original.",
            "Same length": "Keep the rewrite roughly the same length as the original."
        }.get(length, "Keep the rewrite roughly the same length as the original.")

        system_instruction = (
            f"You are Copilot's text rewriting engine, built into Microsoft Edge. "
            f"Rewrite the user's text in a '{tone}' tone. {length_hint} "
            f"Preserve the original meaning while improving clarity and flow. "
            f"Additional instructions to prioritize: {extra_instructions or 'none'}"
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=source_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            )
        )

        st.session_state.cop_text = response.text
        st.session_state.cop_rewritten = True
        st.session_state.cop_version += 1
        placeholder.empty()
        st.rerun()

    except KeyError:
        placeholder.empty()
        st.error("🔒 'GEMINI_API_KEY' not found in secrets.")
    except Exception as e:
        placeholder.empty()
        st.error(f"Copilot couldn't rewrite this: {str(e)}")


if rewrite_button:
    if st.session_state.cop_original is None:
        st.session_state.cop_original = current_text
    do_rewrite(current_text)

if regenerate_button:
    do_rewrite(st.session_state.cop_original or current_text)

if undo_button:
    st.session_state.cop_text = st.session_state.cop_original or ""
    st.session_state.cop_rewritten = False
    st.session_state.cop_version += 1
    st.rerun()