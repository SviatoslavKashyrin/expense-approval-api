import time
from typing import Dict, Any


def analyze_expense_data(description: str, amount: float) -> Dict[str, Any]:
    time.sleep(5)


    is_suspicious = amount > 1000

    return {
        "ai_status": "completed",
        "ai_flag": is_suspicious,
        "ai_flag_reason": "Занадто велика сума для автоматичного схвалення" if is_suspicious else None,
        "ai_summary": f"Згенерований звіт: {description[:30]}..."
    }