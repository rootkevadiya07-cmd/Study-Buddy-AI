# StudyBuddy AI — Your Personal AI Study Partner 🎓

> **Built for the Hacktoberfest Weekend Challenge: Build for a Friend**

StudyBuddy AI is a production-grade, open-source AI study partner designed to help college students easily comprehend lengthy lecture notes, generate structured revision guides, practice exam-level MCQs, create customized daily study schedules, and test their knowledge with interactive quizzes.

## 📸 Live Preview & Demo

### 📹 Interactive Tool Walkthrough
![StudyBuddy AI Walkthrough Demo](assets/studybuddy_walkthrough.webp)

### 📸 Streamlit Dashboard Preview
![StudyBuddy AI Streamlit Interface](assets/dashboard_preview.png)

---

## 📖 Built for a Friend

> *"I built StudyBuddy AI for my college friend **[Friend's Name]**, a B.Tech Computer Science student who spends hours reading 100+ page lecture PDFs before exams. They needed a privacy-focused, intelligent study assistant that could answer questions directly from their notes, explain difficult algorithms in simple terms, and create quick daily study schedules without relying on generic subscription chatbots."*

---

## 🚀 Key Features

1. **💬 Ask My Notes (RAG Chat)**: Semantic Q&A strictly grounded in uploaded PDF study material. Never hallucinates outside your notes.
2. **🎈 Explain Like I'm 10 (ELI5)**: Simplifies complex technical terms using intuitive real-world analogies and practical examples.
3. **📝 Generate Summary**: Creates high-yield chapter summaries, key definitions, and exam cheat sheets.
4. **❓ Generate MCQs**: Generates 5, 10, or 20 multiple-choice questions with answer keys and short explanations.
5. **🎯 Important Questions**: Extracts high-probability exam questions categorized into Very Important, Important, and Practice.
6. **📅 Personalized Study Plan**: Builds a day-by-day study schedule based on your exam date, daily hours, and subject syllabus.
7. **🧪 Interactive Quiz Mode**: Step-by-step quiz testing with real-time scorecards and question explanations.
8. **💡 Open AI Architecture**: Full support for local offline inference via Ollama or cloud open-weight APIs (Groq, OpenRouter).

---

## 🏗️ Application Architecture

```
User (Browser)
   │
   ▼
Streamlit UI (app.py)
   │
   ├──► PDF Processing (pdf_reader.py - PyMuPDF)
   │       │
   │       ▼
   ├──► Text Chunking & Embeddings (rag.py - Sentence Transformers)
   │       │
   │       ▼
   ├──► Vector Database (FAISS IndexFlatIP)
   │       │
   │       ▼
   ├──► AI Service Abstraction Layer (ai.py)
   │       ├──► LOCAL MODE: Ollama (llama3.2 / mistral)
   │       └──► DEPLOYED MODE: Open-Weight API (Groq / OpenRouter)
   │
   ▼
AI Response Output
```

---

## 🛠️ Technology Stack

- **Frontend & UI**: Streamlit (Python)
- **PDF Extraction**: PyMuPDF (`fitz`)
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Vector Storage**: FAISS (`faiss-cpu`)
- **AI Core**: Open-weight LLMs (Llama 3.2, Mistral, Gemma 2, Qwen 2.5)
- **Local Engine**: Ollama HTTP API
- **Deployment**: Render Web Service
- **Source Control**: GitHub

---

## 💡 Why Open Innovation Matters

StudyBuddy AI is built around open-weight models to guarantee transparency and control:
- **Local Privacy**: Your personal college notes stay on your machine when running Ollama.
- **Model Swapping**: Easily switch models (e.g. `llama3.2`, `mistral`, `phi3`) in 1 click.
- **Zero API Lock-in**: Works offline without vendor dependence or expensive subscription tiers.

---

## 💻 Local Installation & Setup

### Prerequisites
- Python 3.9+ installed
- Git installed

### 1. Clone & Setup Virtual Environment
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/StudyBuddy-AI.git
cd StudyBuddy-AI

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` according to your preferred mode:
```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

---

## 🦙 Ollama Local Setup (Step-by-Step)

To run StudyBuddy AI 100% locally with private AI inference:

1. **Install Ollama**: Download from [https://ollama.com](https://ollama.com)
2. **Download Model**: Open terminal and run:
   ```bash
   ollama pull llama3.2
   ```
3. **Start Ollama Server**:
   ```bash
   ollama serve
   ```
4. **Run StudyBuddy AI**:
   ```bash
   streamlit run app.py
   ```
5. Open `http://localhost:8501` in your browser!

---

## 🌐 Render Deployment Instructions

To deploy StudyBuddy AI on Render:

1. **Push Code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for StudyBuddy AI"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/StudyBuddy-AI.git
   git push -u origin main
   ```
2. **Create Render Account**: Sign up at [https://render.com](https://render.com)
3. **New Web Service**:
   - Click **New +** -> **Web Service**
   - Connect your GitHub repository (`StudyBuddy-AI`)
4. **Configure Settings**:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. **Add Environment Variables**:
   - `AI_PROVIDER`: `openai_compatible`
   - `API_BASE_URL`: `https://api.groq.com/openai/v1`
   - `MODEL_NAME`: `llama-3.1-8b-instant`
   - `API_KEY`: *Your Groq/OpenRouter API key*
6. **Deploy**: Click **Deploy Web Service** and access your live URL!

---

## ❓ Troubleshooting

- **Ollama Connection Error**: Verify `ollama serve` is running and `http://localhost:11434` is accessible.
- **Empty PDF Error**: Ensure your uploaded PDF contains selectable text (not scanned images).
- **FAISS Installation Issue**: Make sure `faiss-cpu` is installed.

---

## 🔮 Future Enhancements
- 🎙️ Voice-guided concept explanations
- 🗂️ Multi-document RAG comparison
- 🎴 Automated flashcard generator (Anki export)

---

## 📜 License
MIT License - Created for Hacktoberfest Weekend Challenge.
