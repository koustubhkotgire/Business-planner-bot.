# Business Idea & Planning Assistant (free tools only)

## Setup in VS Code
1. Open this folder in VS Code (File > Open Folder). Install the **Python** extension.
2. Open the terminal (Ctrl+`) and run:
   ```
   python -m venv venv
   venv\Scripts\activate          # Windows
   source venv/bin/activate       # macOS/Linux
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and paste your free API key (or enter it in the app sidebar).
4. Run: `streamlit run app.py` (or press F5, "Run Streamlit app").

## Free providers
- Groq: console.groq.com/keys
- Google Gemini: aistudio.google.com/apikey
- OpenRouter: openrouter.ai/keys (choose models ending in `:free`)
- Ollama (offline): install from ollama.com, run `ollama pull llama3.1`, no key needed.

## Files
- app.py       Streamlit UI and conversation flow
- llm.py       Provider-agnostic LLM client
- prompts.py   System, plan and profile prompts
- search.py    Free DuckDuckGo web search
- exporter.py  Markdown -> Word (.docx)

## Deploy free
Push to GitHub, deploy on Streamlit Community Cloud, add LLM_API_KEY under Secrets
(secrets are exposed as environment variables).
