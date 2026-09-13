import json
from typing import Dict, Any
from google import genai
from google.genai import types
from app.core.config import settings


client = genai.Client(api_key=settings.GEMINI_API_KEY)


def analyze_expense_data(description: str, amount: float) -> Dict[str, Any]:
    prompt = f"""
    Проаналізуй фінансову заявку співробітника.
    Сума: {amount}
    Опис: {description}

    Поверни відповідь СУВОРО у форматі JSON з такими ключами:
    - ai_status: завжди "completed"
    - ai_flag: boolean (true, якщо витрата виглядає неробочою, особистою або сума аномальна для бізнесу, інакше false)
    - ai_flag_reason: рядок з поясненням підозри (або null, якщо ai_flag = false)
    - ai_summary: короткий опис суті заявки (1-2 речення)
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        return {
            "ai_status": "error",
            "ai_flag": False,
            "ai_flag_reason": str(e),
            "ai_summary": "Не вдалося отримати аналіз від AI."
        }