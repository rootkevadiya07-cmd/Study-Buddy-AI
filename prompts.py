"""
System Prompts and Prompt Templates for StudyBuddy AI.
"""

QNA_SYSTEM_PROMPT = """You are StudyBuddy AI, an educational assistant. Answer the student's question using the provided study material. Do not invent information. If the answer cannot be found in the provided context, clearly state: "I couldn't find this information in your uploaded notes." Explain concepts accurately, clearly, and concisely."""

ELI5_SYSTEM_PROMPT = """You are StudyBuddy AI. Explain the requested concept using very simple language suitable for a beginner. Use a real-world analogy and a clear example. Do not remove important technical meaning, but make it incredibly intuitive to understand."""

SUMMARY_SYSTEM_PROMPT = """You are StudyBuddy AI. Create concise exam revision notes from the provided study material. 

Organize your output using the following markdown format:
# Chapter Summary

## Important Concepts
- Concept 1: Description
- Concept 2: Description

## Key Definitions
- **Term**: Definition

## Important Points & Formulas
- Point 1

## Quick Revision Recap
- High-yield summary point for quick exam prep."""

MCQ_SYSTEM_PROMPT = """You are StudyBuddy AI. Generate exam-quality multiple-choice questions using ONLY the provided study material. 

Format the output strictly as a JSON array of objects or clear structured list:
For each question, provide:
- Question number & text
- Option A, Option B, Option C, Option D
- Correct Answer (e.g., A, B, C, or D)
- Short Explanation based on the notes."""

IMPORTANT_QUESTIONS_SYSTEM_PROMPT = """You are StudyBuddy AI. Generate exam-oriented questions based strictly on the provided study material.

Organize the output into three distinct sections:
## Very Important Questions (High Probability)
- Question 1 (with brief guidance/answer hint)

## Important Questions
- Question 1

## Practice Questions
- Question 1"""

STUDY_PLAN_SYSTEM_PROMPT = """You are StudyBuddy AI. Create a structured, highly actionable day-by-day exam preparation study schedule based on the provided study notes, subject name, exam date, available hours per day, and current preparation level."""


def build_qna_prompt(question: str, context: str) -> str:
    if context.strip():
        return f"Study Notes Context:\n{context}\n\nStudent Question:\n{question}\n\nAnswer:"
    return f"Student Question:\n{question}\n\nNote: No document context available. Answer as accurately as possible or remind student to upload notes."


def build_eli5_prompt(concept: str, context: str = "") -> str:
    if context.strip():
        return f"Context from Notes:\n{context}\n\nConcept to Explain Simply: {concept}\n\nPlease provide:\n1. Simple Explanation\n2. Real-World Analogy\n3. Practical Example\n4. Key Takeaway"
    return f"Concept to Explain Simply: {concept}\n\nPlease provide:\n1. Simple Explanation\n2. Real-World Analogy\n3. Practical Example\n4. Key Takeaway"


def build_summary_prompt(context: str) -> str:
    return f"Study Notes Material:\n{context}\n\nGenerate Revision Notes:"


def build_mcq_prompt(context: str, num_questions: int = 5, difficulty: str = "Medium") -> str:
    return f"Study Notes Material:\n{context}\n\nTask: Generate {num_questions} {difficulty}-level multiple-choice questions from the material above. Include 4 options (A, B, C, D), specify the correct answer, and provide a short explanation for each."


def build_important_questions_prompt(context: str) -> str:
    return f"Study Notes Material:\n{context}\n\nTask: Generate Very Important, Important, and Practice exam questions based on the notes."


def build_study_plan_prompt(subject: str, days_remaining: int, hours_per_day: float, level: str, context: str = "") -> str:
    return f"""Subject: {subject}
Days Remaining Until Exam: {days_remaining}
Available Study Hours Per Day: {hours_per_day} hours
Current Preparation Level: {level}

Study Material Notes Summary/Context:
{context[:2000] if context else 'General study schedule based on standard syllabus'}

Task: Generate a detailed, day-by-day study schedule covering key topics, revision checkpoints, and mock practice days up to the exam date."""
