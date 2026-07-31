import streamlit as st
from google import genai
from google.genai import types

# 1. UI Configuration
st.set_page_config(page_title="Copilot Rewrite Studio (Gemini)", layout="wide", page_icon="📝")

# Modern layout spacing and aesthetic formatting
st.markdown("""
    <style>
    .stTextArea textarea { font-size: 15px !important; border-radius: 8px !important; }
    div[data-testid="stNotification"] { background-color: #f0f7ff !important; border-left: 5px solid #4a90e2 !important; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("📝 Copilot Text Rewriter")
st.caption("Powered by Google Gemini — Free personal deployment pipeline.")

# 2. Sidebar Configuration
with st.sidebar:
    st.header("🎭 Tone Options")
    tone = st.selectbox(
        "Select Profile:",
        ["💼 Professional & Formal", "🤝 Casual & Friendly", "⚡ Concise & Short", "🎨 Creative & Engaging"]
    )
    extra_instructions = st.text_input("Custom rules (e.g., 'Convert into bullet points'):")

# 3. Main Split View Layout
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📥 Original Text")
    user_text = st.text_area("Your text:", height=250, placeholder="Paste text here...", label_visibility="collapsed")
    submit_button = st.button("✨ Rewrite Text", type="primary", use_container_width=True)

with col2:
    st.markdown("### 📤 Copilot Rewrite")
    
    if submit_button:
        if not user_text.strip():
            st.warning("Please type some text first.")
        else:
            with st.spinner("Gemini is processing your rewrite..."):
                try:
                    # Securely pull API Key from Streamlit Secrets vault
                    gemini_key = st.secrets["GEMINI_API_KEY"]
                    
                    # Instantiate Google GenAI Client
                    client = genai.Client(api_key=gemini_key)
                    
                    # Formulate system prompts matching Copilot's style constraints
                    system_instruction = (
                        f"You are an expert copywriter acting as an AI Copilot rewriting engine. "
                        f"Your task is to rewrite the user's text to fit a '{tone}' tone. "
                        f"Ensure the rewritten version preserves the original core meaning while vastly improving vocabulary, "
                        f"flow, and formatting. Additional rules to prioritize: {extra_instructions}"
                    )
                    
                    # Call Gemini 1.5 Flash Model
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=user_text,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.7
                        )
                    )
                    
                    # Render outputs
                    rewritten_result = response.text
                    st.text_area("Result:", value=rewritten_result, height=250, label_visibility="collapsed")
                    st.success("🎉 Successfully rewritten!")
                    
                except KeyError:
                    st.error("🔒 Key Configuration Error: 'GEMINI_API_KEY' not found in system secrets.")
                except Exception as e:
                    st.error(f"Google API Error: {str(e)}")
    else:
        st.info("The rewritten layout will generate here.")
