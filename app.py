import streamlit as st
import os
from datetime import date, timedelta
from config import Config
from pdf_reader import process_pdf_bytes
from rag import RAGPipeline
from ai import ai_service
import prompts
from study_plan import generate_study_plan
from quiz import generate_quiz_questions, QuizSession

# Page Config
st.set_page_config(
    page_title="StudyBuddy AI — Your Personal AI Study Partner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern, WOW Aesthetics
st.markdown("""
<style>
    /* Custom Styling */
    .main-header {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0px;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    .stat-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-success {
        background-color: #065f46;
        color: #34d399;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-warning {
        background-color: #78350f;
        color: #fbbf24;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .chat-bubble-user {
        background-color: #312e81;
        color: #e0e7ff;
        padding: 12px 16px;
        border-radius: 16px 16px 2px 16px;
        margin-bottom: 10px;
        max-width: 85%;
        margin-left: auto;
    }
    .chat-bubble-ai {
        background-color: #1e293b;
        border: 1px solid #334155;
        color: #f1f5f9;
        padding: 12px 16px;
        border-radius: 16px 16px 16px 2px;
        margin-bottom: 10px;
        max-width: 85%;
    }
    .context-box {
        background-color: #0f172a;
        border-left: 4px solid #6366f1;
        padding: 10px 14px;
        font-size: 0.88rem;
        color: #cbd5e1;
        margin-top: 8px;
        border-radius: 0 6px 6px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State Variables
if "rag" not in st.session_state:
    st.session_state.rag = RAGPipeline()
if "doc_meta" not in st.session_state:
    st.session_state.doc_meta = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "quiz_session" not in st.session_state:
    st.session_state.quiz_session = None

# Sidebar Content
with st.sidebar:
    st.markdown("## 🎓 StudyBuddy AI")
    st.markdown("*Your Personal AI Study Partner*")
    st.markdown("---")
    
    # PDF File Uploader
    uploaded_file = st.file_uploader("📂 Upload Study Material (PDF)", type=["pdf"], help="Upload your college lecture notes, chapter PDFs, or revision guides.")
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        # Process if new file or not processed yet
        if st.session_state.doc_meta is None or st.session_state.doc_meta.get("filename") != uploaded_file.name:
            with st.spinner("Processing PDF text & building semantic index..."):
                res = process_pdf_bytes(file_bytes, filename=uploaded_file.name)
                if res["success"]:
                    build_res = st.session_state.rag.build_index(res["text"])
                    if build_res["success"]:
                        st.session_state.doc_meta = {
                            "filename": res["filename"],
                            "pages": res["page_count"],
                            "chars": res["char_count"],
                            "chunks": build_res["num_chunks"],
                            "text": res["text"]
                        }
                        st.success(f"Loaded '{uploaded_file.name}'!")
                    else:
                        st.error(f"Vector Indexing Error: {build_res.get('error')}")
                else:
                    st.error(f"PDF Error: {res.get('error')}")
                    
    # Document Metadata Summary
    if st.session_state.doc_meta:
        st.markdown("### 📄 Document Status")
        st.markdown(f"**File:** `{st.session_state.doc_meta['filename']}`")
        st.markdown(f"**Pages:** {st.session_state.doc_meta['pages']} | **Chunks:** {st.session_state.doc_meta['chunks']}")
        st.markdown(f"**Text Size:** {st.session_state.doc_meta['chars']:,} chars")
        st.markdown('<span class="badge-success">✓ Vector Store Ready</span>', unsafe_allow_html=True)
    else:
        st.info("💡 Please upload a PDF file to unlock RAG features.")
        
    st.markdown("---")
    
    # Student Settings
    st.markdown("### 🗓️ Exam Planning")
    subject_name = st.text_input("Subject Name", value="Computer Networks")
    exam_date_val = st.date_input("Exam Date", value=date.today() + timedelta(days=7))
    study_hours = st.slider("Daily Study Hours", min_value=1.0, max_value=12.0, value=3.0, step=0.5)
    prep_level = st.selectbox("Current Prep Level", ["Beginner", "Intermediate", "Advanced"])

    st.markdown("---")
    
    # AI Backend Status Indicator
    st.markdown("### ⚡ AI Backend Status")
    provider_info = Config.get_provider_info()
    st.caption(f"**Mode:** {provider_info['mode']}")
    st.caption(f"**Model:** `{provider_info['target']}`")
    
    status_check = ai_service.check_connection()
    if status_check["connected"]:
        st.markdown('<span class="badge-success">● AI Engine Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-warning">▲ Offline Fallback Active</span>', unsafe_allow_html=True)
        st.caption(status_check.get("suggestion", ""))

# Main Dashboard Header
st.markdown('<h1 class="main-header">StudyBuddy AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your Personal Open-Source AI Study Partner for Exam Success</p>', unsafe_allow_html=True)

# Overview Dashboard Stats Bar
col1, col2, col3, col4 = st.columns(4)
with col1:
    pages_str = str(st.session_state.doc_meta['pages']) if st.session_state.doc_meta else "0"
    st.markdown(f'<div class="stat-card"><div class="stat-value">{pages_str}</div><div class="stat-label">PDF Pages</div></div>', unsafe_allow_html=True)
with col2:
    chunks_str = str(st.session_state.doc_meta['chunks']) if st.session_state.doc_meta else "0"
    st.markdown(f'<div class="stat-card"><div class="stat-value">{chunks_str}</div><div class="stat-label">Indexed Chunks</div></div>', unsafe_allow_html=True)
with col3:
    days_left = max(0, (exam_date_val - date.today()).days)
    st.markdown(f'<div class="stat-card"><div class="stat-value">{days_left}</div><div class="stat-label">Days to Exam</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{study_hours}h</div><div class="stat-label">Daily Hours</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Feature Navigation Tabs
tab_chat, tab_eli5, tab_summary, tab_mcq, tab_questions, tab_plan, tab_quiz, tab_open_ai = st.tabs([
    "💬 Ask My Notes",
    "🎈 Explain Simply",
    "📝 Generate Summary",
    "❓ Generate MCQs",
    "🎯 Important Questions",
    "📅 Study Plan",
    "🧪 Quiz Mode",
    "💡 Why Open AI?"
])

# ---------------------------------------------------------
# TAB 1: ASK MY NOTES (RAG CHAT)
# ---------------------------------------------------------
with tab_chat:
    st.subheader("💬 Ask Questions About Your Uploaded Notes")
    st.caption("Answers are strictly grounded in retrieved segments from your study material.")
    
    if not st.session_state.doc_meta:
        st.warning("⚠️ Please upload a PDF study note in the sidebar to start asking questions!")
    else:
        # Display Chat History
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user"><b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-ai"><b>StudyBuddy:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
                if "context" in msg and msg["context"]:
                    with st.expander("🔍 Based on your uploaded notes (Retrieved Context)"):
                        st.markdown(f'<div class="context-box">{msg["context"]}</div>', unsafe_allow_html=True)

        # Chat Input Box
        user_query = st.chat_input("Ask anything from your uploaded PDF notes...")
        if user_query:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # Retrieve relevant context from FAISS RAG pipeline
            with st.spinner("Searching document context & generating response..."):
                retrieved_context = st.session_state.rag.get_formatted_context(user_query, top_k=3)
                
                if not retrieved_context.strip():
                    ai_answer = "I couldn't find this information in your uploaded notes."
                else:
                    prompt = prompts.build_qna_prompt(user_query, retrieved_context)
                    ai_answer = ai_service.generate(
                        prompt=prompt,
                        context=retrieved_context,
                        system_prompt=prompts.QNA_SYSTEM_PROMPT
                    )
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": ai_answer,
                    "context": retrieved_context
                })
                
                st.rerun()

# ---------------------------------------------------------
# TAB 2: EXPLAIN LIKE I'M 10 (ELI5)
# ---------------------------------------------------------
with tab_eli5:
    st.subheader("🎈 Explain Like I'm 10 (ELI5)")
    st.caption("Simplify complex terms using clear real-world analogies and beginner examples.")
    
    concept_input = st.text_input("Enter a concept or topic from your notes:", placeholder="e.g. Binary Search, TCP 3-Way Handshake, Polymorphism")
    
    if st.button("✨ Explain Simply", type="primary"):
        if not concept_input.strip():
            st.error("Please enter a concept name to explain.")
        else:
            with st.spinner(f"Simplifying '{concept_input}'..."):
                doc_context = ""
                if st.session_state.doc_meta:
                    doc_context = st.session_state.rag.get_formatted_context(concept_input, top_k=2)
                    
                prompt = prompts.build_eli5_prompt(concept_input, doc_context)
                explanation = ai_service.generate(
                    prompt=prompt,
                    context=doc_context,
                    system_prompt=prompts.ELI5_SYSTEM_PROMPT
                )
                
                st.markdown("### 🌟 Simplified Explanation")
                st.info(explanation)

# ---------------------------------------------------------
# TAB 3: GENERATE SUMMARY
# ---------------------------------------------------------
with tab_summary:
    st.subheader("📝 Quick Exam Revision Summary")
    st.caption("Extract key definitions, formulas, and structured revision points from your PDF notes.")
    
    if not st.session_state.doc_meta:
        st.warning("⚠️ Please upload a PDF note to generate revision summaries.")
    else:
        if st.button("⚡ Generate Chapter Summary", type="primary"):
            with st.spinner("Extracting high-yield concepts & generating summary..."):
                # Sample context from top chunks / full text
                context_sample = st.session_state.doc_meta["text"][:4000]
                prompt = prompts.build_summary_prompt(context_sample)
                summary_output = ai_service.generate(
                    prompt=prompt,
                    context=context_sample,
                    system_prompt=prompts.SUMMARY_SYSTEM_PROMPT
                )
                
                st.markdown(summary_output)
                st.download_button(
                    label="💾 Download Summary (.md)",
                    data=summary_output,
                    file_name=f"Summary_{st.session_state.doc_meta['filename']}.md",
                    mime="text/markdown"
                )

# ---------------------------------------------------------
# TAB 4: GENERATE MCQS
# ---------------------------------------------------------
with tab_mcq:
    st.subheader("❓ Multiple Choice Question Generator")
    st.caption("Generate exam-style MCQs with 4 options, answer keys, and detailed explanations.")
    
    if not st.session_state.doc_meta:
        st.warning("⚠️ Please upload a PDF note first.")
    else:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            num_mcqs = st.selectbox("Number of Questions", [5, 10, 20], index=0)
        with col_m2:
            difficulty_mcq = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=1)
            
        if st.button("🎲 Generate MCQs", type="primary"):
            with st.spinner("Analyzing document and creating MCQs..."):
                context_sample = st.session_state.doc_meta["text"][:5000]
                prompt = prompts.build_mcq_prompt(context_sample, num_questions=num_mcqs, difficulty=difficulty_mcq)
                mcq_res = ai_service.generate(
                    prompt=prompt,
                    context=context_sample,
                    system_prompt=prompts.MCQ_SYSTEM_PROMPT
                )
                
                st.markdown(mcq_res)

# ---------------------------------------------------------
# TAB 5: IMPORTANT QUESTIONS
# ---------------------------------------------------------
with tab_questions:
    st.subheader("🎯 High-Yield Exam Questions")
    st.caption("Categorized exam questions derived from your study material.")
    
    if not st.session_state.doc_meta:
        st.warning("⚠️ Please upload a PDF note to extract important questions.")
    else:
        if st.button("🔥 Generate Exam Questions", type="primary"):
            with st.spinner("Identifying high-yield exam topics..."):
                context_sample = st.session_state.doc_meta["text"][:5000]
                prompt = prompts.build_important_questions_prompt(context_sample)
                imp_questions = ai_service.generate(
                    prompt=prompt,
                    context=context_sample,
                    system_prompt=prompts.IMPORTANT_QUESTIONS_SYSTEM_PROMPT
                )
                
                st.markdown(imp_questions)

# ---------------------------------------------------------
# TAB 6: STUDY PLANNER
# ---------------------------------------------------------
with tab_plan:
    st.subheader("📅 Personalized Exam Study Plan")
    st.caption("Custom day-by-day timetable based on your exam date, daily hours, and subject syllabus.")
    
    st.markdown(f"**Subject:** `{subject_name}` | **Days Remaining:** `{days_left}` | **Daily Goal:** `{study_hours} hrs/day` | **Level:** `{prep_level}`")
    
    if st.button("🚀 Generate My Study Plan", type="primary"):
        with st.spinner("Calculating schedule and topic distribution..."):
            doc_context = st.session_state.doc_meta["text"][:3000] if st.session_state.doc_meta else ""
            plan_res = generate_study_plan(
                subject=subject_name,
                exam_date=exam_date_val.strftime("%Y-%m-%d"),
                hours_per_day=study_hours,
                preparation_level=prep_level,
                context=doc_context
            )
            st.markdown(plan_res)

# ---------------------------------------------------------
# TAB 7: INTERACTIVE QUIZ MODE
# ---------------------------------------------------------
with tab_quiz:
    st.subheader("🧪 Interactive AI Quiz Mode")
    st.caption("Test your preparation level with an interactive step-by-step test.")
    
    if not st.session_state.doc_meta:
        st.warning("⚠️ Please upload a PDF note to enable interactive quiz mode.")
    else:
        if st.session_state.quiz_session is None or st.button("🔄 Start New Quiz"):
            with st.spinner("Generating quiz questions from your notes..."):
                doc_context = st.session_state.doc_meta["text"][:4000]
                questions = generate_quiz_questions(doc_context, num_questions=5, difficulty="Medium")
                st.session_state.quiz_session = QuizSession(questions)
                st.rerun()
                
        q_session = st.session_state.quiz_session
        if q_session and len(q_session.questions) > 0:
            if not q_session.completed:
                st.progress((q_session.current_index + 1) / len(q_session.questions))
                st.markdown(f"### Question {q_session.current_index + 1} of {len(q_session.questions)}")
                
                curr_q = q_session.questions[q_session.current_index]
                st.write(f"**{curr_q['question']}**")
                
                opts = curr_q["options"]
                opt_keys = list(opts.keys())
                
                choice = st.radio(
                    "Select your answer:",
                    opt_keys,
                    format_func=lambda k: f"{k}. {opts[k]}"
                )
                
                col_prev, col_next = st.columns([1, 1])
                with col_next:
                    if st.button("Submit Answer ➔"):
                        q_session.submit_answer(q_session.current_index, choice)
                        if q_session.current_index + 1 < len(q_session.questions):
                            q_session.current_index += 1
                        else:
                            q_session.completed = True
                        st.rerun()
            else:
                st.markdown("## 🎉 Quiz Completed!")
                score_meta = q_session.get_score_summary()
                
                sc_col1, sc_col2, sc_col3 = st.columns(3)
                sc_col1.metric("Score Percentage", f"{score_meta['score_percentage']}%")
                sc_col2.metric("Correct Answers", f"{score_meta['correct_answers']}/{score_meta['total_questions']}")
                sc_col3.metric("Wrong Answers", f"{score_meta['wrong_answers']}")
                
                st.markdown("---")
                st.markdown("### 🔍 Question Breakdown & Explanations")
                
                for item in score_meta["breakdown"]:
                    status_icon = "✅ Correct" if item["is_correct"] else "❌ Incorrect"
                    with st.expander(f"Question {item['question_num']}: {status_icon}"):
                        st.write(f"**Question:** {item['question']}")
                        st.write(f"**Your Answer:** {item['user_answer']}")
                        st.write(f"**Correct Answer:** {item['correct_answer']}")
                        st.info(f"**Explanation:** {item['explanation']}")

# ---------------------------------------------------------
# TAB 8: WHY OPEN INNOVATION MATTERS
# ---------------------------------------------------------
with tab_open_ai:
    st.subheader("💡 Why Open Innovation Matters")
    st.markdown("""
    ### Built on Open-Weight AI Architecture

    StudyBuddy AI is intentionally designed around **open-weight models** (such as Llama 3, Mistral, Gemma, and Qwen) rather than proprietary black-box APIs.

    #### 🌟 Key Benefits of Open AI for Students:
    1. **Data Privacy & Security**: Your private college notes and study materials remain on your local device when running via Ollama.
    2. **Model Flexibility**: Swap models effortlessly (e.g., from `llama3.2` to `mistral` or `qwen2.5`) without changing your code.
    3. **Zero API Lock-in**: Complete independence from expensive subscription tiers or rate limits.
    4. **Offline Capability**: Study anywhere—even without an internet connection using local Ollama inference.
    
    #### ⚙️ Deployment Modes:
    - **LOCAL MODE**: Students run open-weight models locally on their laptop via [Ollama](https://ollama.ai).
    - **DEPLOYED MODE**: Render web service connects to configured open-weight API endpoints (like Groq or OpenRouter) using standard open AI protocols.
    """)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b;'>StudyBuddy AI — Hacktoberfest Weekend Challenge: Build for a Friend | Open-Weight AI</p>", unsafe_allow_html=True)
