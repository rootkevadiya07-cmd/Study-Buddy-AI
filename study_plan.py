from datetime import datetime, date
from typing import Dict, Any
from ai import ai_service
import prompts

def calculate_days_remaining(exam_date: str) -> int:
    """Calculate remaining days until exam date string (YYYY-MM-DD)."""
    try:
        target = datetime.strptime(exam_date, "%Y-%m-%d").date()
        today = date.today()
        delta = (target - today).days
        return max(1, delta)
    except Exception:
        return 7  # Default 7 days if date parsing fails

def generate_study_plan(
    subject: str,
    exam_date: str,
    hours_per_day: float,
    preparation_level: str = "Intermediate",
    context: str = ""
) -> str:
    """
    Generates a personalized daily study plan based on exam date,
    available daily hours, preparation level, and document context.
    """
    days_remaining = calculate_days_remaining(exam_date)
    
    prompt = prompts.build_study_plan_prompt(
        subject=subject,
        days_remaining=days_remaining,
        hours_per_day=hours_per_day,
        level=preparation_level,
        context=context
    )
    
    plan = ai_service.generate(
        prompt=prompt,
        context=context,
        system_prompt=prompts.STUDY_PLAN_SYSTEM_PROMPT
    )
    
    return plan
