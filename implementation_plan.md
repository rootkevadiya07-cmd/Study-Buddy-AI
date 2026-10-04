# Implementation Plan - StudyBuddy AI

Build a complete, production-ready student AI application called **StudyBuddy AI — Your Personal AI Study Partner** for the Hacktoberfest Weekend Challenge: Build for a Friend.

## User Review Required

> [!NOTE]
> The project will use **PyMuPDF** (`fitz`) for PDF text extraction, **Sentence Transformers** (`all-MiniLM-L6-v2`) + **FAISS** (`faiss-cpu`) for vector retrieval, and a modular AI service supporting **Ollama** (Local Mode) and **OpenAI-compatible / Open-Weight APIs** (Groq, OpenRouter, HuggingFace) for Production Mode on **Render**.

## Proposed Changes

We will create a modular Python project structure in the workspace root directory:

```
c:\Users\hitva\OneDrive\Desktop\Hacktoberfest Weekend Challenge
├── config.py             # Centralized config (Env variables, LLM provider settings)
├── pdf_reader.py         # PDF text extraction & validation using PyMuPDF
├── rag.py                # Text chunking, SentenceTransformers embedding, FAISS index
├── ai.py                 # Multi-backend LLM abstraction layer (Ollama, Groq, OpenRouter, fallback)
├── prompts.py            # Optimized educational system prompts for RAG, ELI5, MCQs, Summaries
├── study_plan.py         # Custom exam study planner generator
├── quiz.py               # Interactive quiz state manager & scorecard evaluator
├── app.py                # Streamlit UI main dashboard & interactive views
├── requirements.txt      # Dependencies list
├── render.yaml           # Render deployment configuration with PORT binding
├── .env.example          # Environment variables template
├── .gitignore            # Git exclusion rules
└── README.md             # Production-grade GitHub README with Hacktoberfest story & guides
```

---

### Key Modules & Responsibilities

#### [NEW] `config.py`
- Load environment variables using `python-dotenv`.
- Manage AI provider settings (`AI_PROVIDER`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `API_KEY`, `API_BASE_URL`).

#### [NEW] `pdf_reader.py`
- Open PDF files with `fitz` (PyMuPDF).
- Extract page-by-page text, calculate character counts, validate non-empty text, handle corrupt files.

#### [NEW] `rag.py`
- Split extracted text into overlapping chunks.
- Compute sentence embeddings via `sentence-transformers`.
- Build and query `FAISS` vector index (`faiss.IndexFlatL2`).
- Retrieve top $k$ relevant context chunks for student queries.

#### [NEW] `ai.py`
- Interface `generate_response(prompt, context=None, system_prompt=None)`.
- Support `ollama` endpoint, `openai_compatible` cloud endpoint (Groq / OpenRouter / Together), and fallback mode.
- Provide `check_ai_status()` to report LLM connectivity status in Streamlit UI sidebar.

#### [NEW] `prompts.py`
- System prompts tailored for educational tasks (Q&A strictly grounded in notes, ELI5 analogies, Structured revision summaries, MCQs, Exam questions).

#### [NEW] `study_plan.py` & `quiz.py`
- Handle business logic for exam preparation schedule generation and step-by-step quiz state.

#### [NEW] `app.py`
- Streamlit application with custom CSS, sidebar configuration, RAG tab, ELI5 tab, Summary tab, MCQ tab, Important Questions tab, Study Plan tab, Interactive Quiz tab, and Open Innovation tab.

#### [NEW] `render.yaml`, `requirements.txt`, `.env.example`, `.gitignore`, `README.md`
- Deployment and configuration files.

---

## Verification Plan

### Automated / Code Verification
1. Verify Python files for syntax errors using `python -m py_compile <file>`.
2. Test PDF extraction, chunking, and FAISS index creation with sample text script in terminal.
3. Test LLM abstraction layer response formatting.

### Manual / UI Verification
1. Launch Streamlit locally: `streamlit run app.py`.
2. Test uploading sample PDF notes.
3. Test all 8 features: Ask My Notes, Explain Simply, Generate Summary, Generate MCQs, Important Questions, Study Plan, Quiz Mode, Why Open Innovation.
4. Verify Render build compatibility (`streamlit run app.py --server.port 8501 --server.address 0.0.0.0`).
