
"""ArtMentor: локальный ИИ-анализ рисунков через Ollama."""

import base64
import requests
import streamlit as st


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3.5:4b"

MODE_LABELS = {
    "realism": "Realism (Re)",
    "character": "Character (Ch)",
    "composition": "Composition (Co)",
}

MODE_PROMPTS = {
    "realism": """
Ты — оператор ArtMentor, специализирующийся на реалистичной живописи и рисунке.

Анализируй:
- форму и объём объектов;
- свет, тени и рефлексы;
- цветовые отношения;
- материалы и фактуры;
- перспективу и пропорции;
- плавность переходов и детализацию.

Учитывай, что работа может быть как законченной, так и находиться в процессе.
Не требуй фотореализма, если автор выбрал стилизацию.
""",

    "character": """
Ты — оператор ArtMentor, специализирующийся на персонажном арте.

Анализируй:
- анатомию и пропорции;
- позу и пластику тела;
- силуэт и читаемость персонажа;
- выразительность лица и эмоций;
- одежду, складки и детали;
- цветовую палитру и рендер;
- стилизацию и визуальную целостность.

Учитывай особенности выбранного художественного стиля.
Не навязывай реалистичную анатомию стилизованным персонажам.
""",

    "composition": """
Ты — оператор ArtMentor, специализирующийся на композиции и пространстве.

Анализируй:
- расположение объектов;
- визуальный баланс;
- перспективу и глубину;
- свет и атмосферу;
- взаимодействие фона и переднего плана;
- цветовые акценты;
- направление взгляда зрителя;
- читаемость и целостность композиции.

Обращай внимание на то, насколько хорошо изображение передаёт задумку автора.
""",
}


def _get_mode_prompt(mode: str) -> str:
    return MODE_PROMPTS.get(
        mode,
        MODE_PROMPTS["character"]
    )


def _check_image(image_bytes: bytes, mime_type: str) -> None:
    if not image_bytes:
        raise ValueError("Изображение пустое.")

    if mime_type not in {
        "image/png",
        "image/jpeg",
        "image/webp",
    }:
        raise ValueError("Формат изображения не поддерживается.")

    if len(image_bytes) > 10 * 1024 * 1024:
        raise ValueError("Изображение превышает лимит 10 МБ.")


def _send_to_ollama(messages: list, timeout: int = 300) -> str:
    """Отправляет запрос локальной модели Ollama."""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "num_ctx": 8192,
                },
            },
            timeout=timeout,
        )

        response.raise_for_status()
        result = response.json()

        content = result.get("message", {}).get("content", "")

        if not content.strip():
            raise RuntimeError("Модель вернула пустой ответ.")

        return content.strip()

    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Не удалось подключиться к Ollama. "
            "Проверь, запущен ли Ollama на компьютере."
        )

    except requests.exceptions.Timeout:
        raise RuntimeError(
            "Модель отвечает слишком долго. Попробуй ещё раз."
        )

    except requests.exceptions.HTTPError as error:
        raise RuntimeError(
            f"Ошибка Ollama: {error}"
        )


def analyze_art(
    image_bytes: bytes,
    mime_type: str,
    mode: str,
    user_goal: str = "",
) -> str:
    """Анализирует рисунок выбранным оператором."""

    _check_image(image_bytes, mime_type)

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    system_prompt = f"""
Ты — ArtMentor, внимательный и профессиональный художественный наставник.
Общайся на русском языке.

{_get_mode_prompt(mode)}

Твоя задача — дать содержательный анализ загруженной работы.

Структура ответа:

## 1. Первое впечатление
Кратко опиши, что изображено и какое впечатление производит работа.

## 2. Что уже хорошо получается
Назови 2–4 конкретные сильные стороны рисунка.

## 3. Что можно улучшить
Укажи до 4 наиболее важных моментов.
Не придумывай ошибки, которых не видно на изображении.

## 4. Как исправить или усилить
Предложи конкретные и понятные способы улучшения.

## 5. Небольшое упражнение
Предложи одно практическое упражнение по теме анализа.

## 6. Итог
Кратко подведи итог и поддержи автора.

ВАЖНЫЕ ПРАВИЛА:
- Не ставь числовые оценки.
- Не сравнивай автора с другими художниками.
- Не выдумывай детали изображения.
- Если что-то невозможно рассмотреть, честно скажи об этом.
- Учитывай художественный стиль и возможную задумку автора.
- Не перегружай ответ профессиональными терминами без объяснения.
"""

    if user_goal.strip():
        user_text = (
            "Дополнительная информация о задумке автора: "
            + user_goal.strip()
            + "\n\nПроанализируй изображение."
        )
    else:
        user_text = "Проанализируй загруженную работу."

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_text,
            "images": [encoded_image],
        },
    ]

    return _send_to_ollama(messages)


def answer_followup(
    image_bytes: bytes,
    mime_type: str,
    mode: str,
    analysis: str,
    conversation: list,
    question: str,
) -> str:
    """Отвечает на дополнительные вопросы по рисунку."""

    _check_image(image_bytes, mime_type)

    if not question or not question.strip():
        raise ValueError("Напиши вопрос перед отправкой.")

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    system_prompt = f"""
Ты — ArtMentor, художественный наставник.
Общайся на русском языке.

Специализация текущего оператора:
{_get_mode_prompt(mode)}

Первоначальный анализ рисунка:
{analysis}

Отвечай на вопросы пользователя, учитывая:
- исходное изображение;
- первоначальный анализ;
- предыдущие сообщения диалога;
- выбранную специализацию оператора.

Правила:
- Отвечай конкретно и понятно.
- Не повторяй весь первоначальный анализ без необходимости.
- Если пользователь просит объяснить, объясняй пошагово.
- Не выдумывай детали, которых не видно на изображении.
- Если информации недостаточно, честно сообщи об этом.
- Не противоречь первоначальному анализу без объяснения причины.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    # Передаём последние сообщения диалога.
    for message in conversation[-12:]:
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content", "")

        if role in {"user", "assistant"} and content:
            messages.append({
                "role": role,
                "content": str(content),
            })

    # Изображение прикладывается к новому вопросу.
    messages.append({
        "role": "user",
        "content": question.strip(),
        "images": [encoded_image],
    })

    return _send_to_ollama(messages)


def main_ai_function(*args, **kwargs):
    """Совместимость со старым интерфейсом проекта."""
    return analyze_art(*args, **kwargs)
