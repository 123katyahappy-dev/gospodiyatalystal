"""ArtMentor: робота з Gemini API (аналіз малюнків і уточнювальний чат)."""

import os
from google import genai
from google.genai import types
import streamlit as st


MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

MODE_PROMPTS = {
    "Realism": """
Ти — ArtMentor Re (Realism), уважний викладач академічного та реалістичного малюнка.
Аналізуй форму, об'єм, пропорції предметів, перспективу, світло й тінь, тональні
відношення, колір, матеріали та інтеграцію об'єктів у середовище.
Не вигадуй помилки, яких не видно. Відрізняй навмисну стилізацію від випадкової
неточності. Пояснюй, чому певне рішення працює або не працює, і давай конкретні
вправи для покращення.
""",
    "Character": """
Ти — ArtMentor Ch (Character), уважний викладач малювання персонажів.
Аналізуй анатомію, пропорції, конструкцію тіла, баланс і позу, силует, жести,
виразність, стилізацію, лінію та рендеринг/покрас. Поважай обраний автором стиль,
зокрема аніме та манґу: не називай стилістичні умовності помилками автоматично.
Не вигадуй деталей, яких не видно. Пояснюй конкретно й доброзичливо.
""",
    "Composition": """
Ти — ArtMentor Co (Composition), уважний викладач композиції та побудови сцени.
Аналізуй розташування елементів, візуальну ієрархію, баланс, перспективу,
глибину простору, фон, освітлення, контраст, напрям погляду та цілісність сцени.
Згадуй золотий перетин лише якщо він справді доречний; не нав'язуй його кожній роботі.
Не вигадуй помилок, яких не видно. Пропонуй конкретні способи покращення.
""",
}

MODE_LABELS = {
    "Realism": "Re · Realism",
    "Character": "Ch · Character",
    "Composition": "Co · Composition",
}


def _get_api_key() -> str:
    """Read the key from Streamlit Secrets or an environment variable."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key
    try:
        return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        return ""


def _client():
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError(
            "Не найден API-ключ Gemini. Добавь GEMINI_API_KEY в .streamlit/secrets.toml "
            "или в Secrets настроек Streamlit Cloud."
        )
    return genai.Client(api_key=api_key)


def _image_part(image_bytes: bytes, mime_type: str):
    if not image_bytes:
        raise ValueError("Изображение пустое. Загрузи файл ещё раз.")
    if mime_type not in {"image/png", "image/jpeg", "image/webp"}:
        raise ValueError("Поддерживаются PNG, JPG и WEBP.")
    return types.Part.from_bytes(data=image_bytes, mime_type=mime_type)


def analyze_art(image_bytes: bytes, mime_type: str, mode: str, user_goal: str = "") -> str:
    """Analyze one uploaded artwork with the selected specialist prompt."""
    if mode not in MODE_PROMPTS:
        raise ValueError("Неизвестный режим ArtMentor.")
    prompt = f"""
{MODE_PROMPTS[mode]}

Сделай структурированный разбор изображения на русском языке.
Учитывай, что это учебная помощь, а не оценка таланта автора.

Используй такую структуру:
## 1. Первое впечатление
Кратко опиши, что видно на работе, и общее впечатление.

## 2. Что уже хорошо получается
Назови 2–4 конкретные сильные стороны, опираясь на изображение.

## 3. Что можно улучшить
Назови до 4 наиболее важных пунктов. Для каждого объясни, что именно заметно
и почему это может влиять на результат. Если явных проблем не видно, честно скажи это.

## 4. Как исправить или усилить
Дай пошаговые, практические рекомендации именно для этой работы.

## 5. Небольшое упражнение
Предложи одно короткое упражнение по главному навыку, который стоит потренировать.

## 6. Итог
Подведи итог в 2–3 предложениях.

Не выставляй числовую оценку и не сравнивай автора с другими художниками.
Если деталь изображения неразборчива, прямо обозначь неопределённость.
Пожелание автора: {user_goal.strip() or "не указано"}.
"""
    response = _client().models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, _image_part(image_bytes, mime_type)],
    )
    result = (response.text or "").strip()
    if not result:
        raise RuntimeError("ИИ не вернул текстовый ответ. Попробуй ещё раз.")
    return result


def answer_followup(
    image_bytes: bytes,
    mime_type: str,
    mode: str,
    analysis: str,
    conversation: list,
    question: str,
) -> str:
    """Answer a follow-up while keeping the same artwork and prior dialogue in context."""
    if mode not in MODE_PROMPTS:
        raise ValueError("Неизвестный режим ArtMentor.")
    if not question.strip():
        raise ValueError("Напиши вопрос перед отправкой.")

    transcript = []
    for item in conversation[-12:]:
        role = "Пользователь" if item.get("role") == "user" else "ArtMentor"
        transcript.append(f"{role}: {item.get('text', '')}")
    transcript_text = "\n".join(transcript) or "Дополнительных сообщений пока нет."

    prompt = f"""
{MODE_PROMPTS[mode]}

Ты продолжаешь разбирать ТОТ ЖЕ рисунок. Ниже исходный анализ и история диалога.
Отвечай на русском, понятно и по делу. Не повторяй весь анализ без необходимости.
Если вопрос выходит за рамки видимого изображения, объясни ограничение.

ИСХОДНЫЙ АНАЛИЗ:
{analysis}

ИСТОРИЯ ДИАЛОГА:
{transcript_text}

НОВЫЙ ВОПРОС ПОЛЬЗОВАТЕЛЯ:
{question}
"""
    response = _client().models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, _image_part(image_bytes, mime_type)],
    )
    result = (response.text or "").strip()
    if not result:
        raise RuntimeError("ИИ не вернул ответ. Попробуй задать вопрос ещё раз.")
    return result


# Совместимость с учебным шаблоном, если где-то ещё вызывается эта функция.
def main_ai_function(user_input):
    return (
        "ArtMentor AI подключается через analyze_art(image_bytes, mime_type, mode). "
        "Выбери направление и загрузи изображение в интерфейсе."
    )
