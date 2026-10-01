import json
import re
import streamlit as st

from llm import PROVIDERS, DEFAULT_KEY, get_client, stream_chat, complete
from prompts import SYSTEM_PROMPT, PLAN_PROMPT, PROFILE_PROMPT, GREETING
from search import web_context
from exporter import markdown_to_docx, markdown_to_pdf

st.set_page_config(page_title="Business Planning Assistant", page_icon="💡", layout="wide")
st.title("💡 Business Idea & Planning Assistant")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("⚙️ Settings")
    st.info("Provider and API settings are hidden for security. Change them in llm.py or your .env file.")
    # Use defaults from llm.py; edit there if you want to change provider/model/api_key/base_url
    provider = list(PROVIDERS)[0]
    base_default, model_default = PROVIDERS[provider]
    api_key = DEFAULT_KEY
    model = model_default
    base_url = base_default
    use_search = st.checkbox("🔎 Use free web search for prices/rules", value=False)
    st.divider()
    make_plan = st.button("📄 Generate business plan", use_container_width=True)
    refresh_profile = st.button("👤 Update my profile summary", use_container_width=True)
    if st.button("🔄 New conversation", use_container_width=True):
        st.session_state.clear()
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": GREETING}]
    st.session_state.plan = None
    st.session_state.profile = {}

if not api_key and "Ollama" not in provider:
    st.info("👈 Add your free API key in the sidebar (or in the .env file) to start.")
    st.stop()

client = get_client(base_url, api_key)


def build_messages(extra_system=None, extra_user=None):
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    if extra_system:
        msgs.append({"role": "system", "content": extra_system})
    msgs += st.session_state.messages
    if extra_user:
        msgs.append({"role": "user", "content": extra_user})
    return msgs


def update_profile():
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.messages)
    try:
        raw = complete(client, model, [
            {"role": "system", "content": PROFILE_PROMPT},
            {"role": "user", "content": transcript[-6000:]},
        ])
        match = re.search(r"\{.*\}", raw, re.S)
        if match:
            st.session_state.profile = json.loads(match.group(0))
    except Exception as e:
        st.sidebar.warning(f"Could not update profile: {e}")


# ---------------- Layout ----------------
chat_col, side_col = st.columns([3, 1])

with side_col:
    st.subheader("Your profile")
    if refresh_profile:
        update_profile()
    if st.session_state.profile:
        for k, v in st.session_state.profile.items():
            st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
    else:
        st.caption("Click “Update my profile summary” after a few messages.")

with chat_col:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Describe your idea, budget, location..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        extra = None
        if use_search:
            loc = st.session_state.profile.get("location", "")
            ctx = web_context(f"{prompt} {loc} cost price licence requirements")
            if ctx:
                extra = "WEB CONTEXT (may be imperfect):\n" + ctx

        with st.chat_message("assistant"):
            reply = st.write_stream(stream_chat(client, model, build_messages(extra_system=extra)))
        st.session_state.messages.append({"role": "assistant", "content": reply})

    if make_plan:
        if len(st.session_state.messages) < 5:
            st.warning("Chat a little more first so the plan can be personalised.")
        else:
            with st.chat_message("assistant"):
                st.session_state.plan = st.write_stream(
                    stream_chat(client, model, build_messages(extra_user=PLAN_PROMPT), temperature=0.5)
                )

    if st.session_state.get("plan"):
        c1, c2 = st.columns(2)
        c1.download_button("⬇️ Download (.md)", st.session_state.plan,
                           file_name="business_plan.md", mime="text/markdown")
        c2.download_button("⬇️ Download (.docx)", markdown_to_docx(st.session_state.plan),
                           file_name="business_plan.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        # Combined PDF export: include full chat transcript and the generated plan
        combined_md = []
        combined_md.append("# Conversation")
        for m in st.session_state.messages:
            role = m.get("role", "user").title()
            combined_md.append(f"**{role}:** {m.get('content','')}")
            combined_md.append("")
        if st.session_state.get("plan"):
            combined_md.append("# Generated Plan")
            combined_md.append(st.session_state.plan)

        pdf_bytes = markdown_to_pdf("\n".join(combined_md))
        c3 = st.download_button("⬇️ Download All (.pdf)", pdf_bytes,
                                file_name="chat_export.pdf",
                                mime="application/pdf")
