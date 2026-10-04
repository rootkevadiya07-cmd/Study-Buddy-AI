import json
import re
from typing import List, Dict, Any
from ai import ai_service
import prompts

def generate_quiz_questions(context: str, num_questions: int = 5, difficulty: str = "Medium") -> List[Dict[str, Any]]:
    """
    Generates structured quiz questions based on the uploaded notes.
    Attempts JSON parsing first, then falls back to robust regex parsing.
    """
    prompt = prompts.build_mcq_prompt(context, num_questions=num_questions, difficulty=difficulty)
    raw_response = ai_service.generate(prompt=prompt, context=context, system_prompt=prompts.MCQ_SYSTEM_PROMPT)
    
    # Try parsing direct JSON
    try:
        # Extract potential JSON block if enclosed in ```json
        json_match = re.search(r'\[.*\]', raw_response, re.DOTALL)
        if json_match:
            questions = json.loads(json_match.group(0))
            if isinstance(questions, list) and len(questions) > 0:
                return questions
    except Exception:
        pass
        
    # Heuristic/Regex parsing if model returns plain text list
    parsed_questions = []
    blocks = re.split(r'\n(?=Question \d+|Q\d+|\d+[\.\)])', raw_response)
    
    for block in blocks:
        if not block.strip():
            continue
            
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        if not lines:
            continue
            
        q_text = lines[0]
        options = {}
        correct_answer = "A"
        explanation = "Based on uploaded study material."
        
        for line in lines[1:]:
            opt_match = re.match(r'^(?:Option\s+)?([A-D])[\.:\)]\s*(.*)', line, re.IGNORECASE)
            if opt_match:
                key = opt_match.group(1).upper()
                options[key] = opt_match.group(2)
            elif "correct" in line.lower() or "answer" in line.lower():
                ans_match = re.search(r'([A-D])', line, re.IGNORECASE)
                if ans_match:
                    correct_answer = ans_match.group(1).upper()
            elif "explanation" in line.lower():
                explanation = line.split(":", 1)[-1].strip()
                
        # Default options if model missed explicit formatting
        if len(options) < 4:
            options = {
                "A": "Option A (Primary concept)",
                "B": "Option B (Secondary concept)",
                "C": "Option C (Alternative theory)",
                "D": "Option D (None of the above)"
            }

        parsed_questions.append({
            "question": q_text,
            "options": options,
            "correct_answer": correct_answer,
            "explanation": explanation
        })

    # Fallback default mock quiz if LLM didn't produce parsed list
    if not parsed_questions:
        parsed_questions = [
            {
                "question": "Q1: What is the primary purpose of study material chunking in RAG?",
                "options": {
                    "A": "To format text into small manageable segments for embedding generation.",
                    "B": "To delete old PDF pages.",
                    "C": "To encrypt student questions.",
                    "D": "To bypass search indexes."
                },
                "correct_answer": "A",
                "explanation": "Chunking splits long documents into smaller segments to maintain semantic focus during vector retrieval."
            },
            {
                "question": "Q2: Which vector search index parameter is commonly used for cosine similarity?",
                "options": {
                    "A": "IndexFlatIP after L2 normalization",
                    "B": "IndexBinaryHash",
                    "C": "RandomForestIndex",
                    "D": "SQLiteSelect"
                },
                "correct_answer": "A",
                "explanation": "Normalizing vector embeddings and using Inner Product (IndexFlatIP) calculates cosine similarity directly."
            }
        ]

    return parsed_questions[:num_questions]


class QuizSession:
    """Manages state and scoring for an interactive student quiz session."""
    
    def __init__(self, questions: List[Dict[str, Any]]):
        self.questions = questions
        self.current_index = 0
        self.user_answers = {}
        self.completed = False

    def submit_answer(self, question_idx: int, selected_option: str):
        """Record answer for a question index."""
        self.user_answers[question_idx] = selected_option.upper()

    def get_score_summary(self) -> Dict[str, Any]:
        """Calculate score percentage and itemized breakdown."""
        total = len(self.questions)
        correct_count = 0
        breakdown = []
        
        for idx, q in enumerate(self.questions):
            user_ans = self.user_answers.get(idx, None)
            is_correct = (user_ans == q["correct_answer"].upper())
            if is_correct:
                correct_count += 1
                
            breakdown.append({
                "question_num": idx + 1,
                "question": q["question"],
                "options": q["options"],
                "user_answer": user_ans,
                "correct_answer": q["correct_answer"],
                "is_correct": is_correct,
                "explanation": q.get("explanation", "")
            })

        score_percent = round((correct_count / total) * 100, 1) if total > 0 else 0
        
        return {
            "total_questions": total,
            "correct_answers": correct_count,
            "wrong_answers": total - correct_count,
            "score_percentage": score_percent,
            "breakdown": breakdown
        }
