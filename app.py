import streamlit as st
from datetime import datetime
from pathlib import Path

from ai_functions import analyze_art, answer_followup, MODE_LABELS
from data_functions import (
    load_data, save_uploaded_image, load_image,
    save_analysis, get_record, update_record
)

st.set_page_config(
    page_title="ArtMentor",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp {
    background: radial-gradient(ellipse at top left, #24213b 0%, #151521 48%, #101018 100%);
    color: #eeeafc;
}
.main .block-container {max-width:1250px; padding-top:2rem; padding-bottom:3rem;}
section[data-testid="stSidebar"] {background:#171622; border-right:1px solid #302b45;}
section[data-testid="stSidebar"] * {color:#e8e3f7;}
.brand {font-size:2.55rem; font-weight:850; letter-spacing:-1.5px; color:#f0eaff;}
.tagline {color:#aaa3c4; font-size:1rem; margin-bottom:1.5rem;}
.intro {
    background:linear-gradient(135deg, #242139 0%, #211e32 100%);
    border:1px solid #39334f; border-radius:18px;
    padding:1.1rem 1.3rem; margin:1rem 0 1.5rem;
}
.intro h3 {color:#f0eaff !important;}
.intro p {color:#bcb5d2 !important;}
.mode-card {
    min-height:230px; background:linear-gradient(160deg,#252238 0%,#1d1b2b 100%);
    border:1px solid #39334f; border-radius:18px; padding:1.1rem;
    box-shadow:0 8px 25px #05050c55;
}
.mode-icon {font-size:1.9rem; margin-bottom:.5rem;}
.mode-title {color:#f0eaff; font-size:1.18rem; font-weight:800; margin-bottom:.4rem;}
.mode-desc {color:#bcb5d2; font-size:.92rem; line-height:1.5;}
div.stButton > button {
    border-radius:11px; border:1px solid #51456f; background:#2b2740;
    color:#e8ddff; font-weight:700; min-height:2.65rem;
}
div.stButton > button:hover {border-color:#a78bfa; color:#fff; background:#3a3156;}
div.stButton > button[kind="primary"] {
    background:#8063c9; border-color:#9b80e5; color:white;
}
div.stButton > button[kind="primary"]:hover {background:#9275dc; border-color:#b39bf0;}
.small-muted {color:#9992b2; font-size:.85rem;}
.stMarkdown, .stText, label, [data-testid="stCaptionContainer"] {color:#e8e3f7;}
[data-testid="stFileUploader"], [data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background:#211f30; color:#eeeafc; border-color:#49415f;
}
[data-testid="stFileUploader"] section {background:#211f30; border-color:#49415f;}
[data-testid="stAlert"] {background:#242137; color:#eeeafc; border:1px solid #39334f;}
[data-testid="stChatMessage"] {background:#211f30; border:1px solid #39334f;}
hr {border-color:#39334f;}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = None
if "current_record_id" not in st.session_state:
    st.session_state.current_record_id = None

MODES = {
    "Realism": {
        "icon": "🖼️",
        "description": "Реалистичный рисунок и живопись: форма, объём, свет, тень, цвет и материалы.",
        "topics": "Реализм · Живопись · Светотень · Цвет",
    },
    "Character": {
        "icon": "✍️",
        "description": "Персонажи в разных стилях: анатомия, пропорции, позы, стилизация и покрас.",
        "topics": "Анатомия · Пози · Стиль · Рендеринг",
    },
    "Composition": {
        "icon": "🏞️",
        "description": "Построение сцены: перспектива, фон, глубина, освещение и композиционный баланс.",
        "topics": "Перспектива · Фон · Свет · Композиция",
    },
}


def open_home():
    st.session_state.page = "home"
    st.session_state.current_record_id = None


def open_workspace(mode):
    st.session_state.selected_mode = mode
    st.session_state.page = "workspace"
    st.session_state.current_record_id = None


def show_header():
    st.markdown('<div class="brand">🖌️ ArtMentor</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="tagline">Твоя творческая мастерская с AI-наставником</div>',
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown("## 🖌️ ArtMentor")
    if st.button("Главная", use_container_width=True):
        open_home()
        st.rerun()
    if st.button("История анализов", use_container_width=True):
        st.session_state.page = "history"
        st.rerun()
    st.divider()
    st.caption("Выбранный оператор")
    selected = st.session_state.selected_mode
    st.write(MODE_LABELS.get(selected, "Пока не выбран") if selected else "Пока не выбран")
    st.caption("Поддерживаются PNG, JPG и WEBP.")


show_header()

if st.session_state.page == "home":
    st.markdown("""
    <div class="intro">
      <h3 style="margin:0 0 .45rem 0;color:#f0eaff;">Твоя творчество — наш общий проект ✨</h3>
      <p style="margin:0;color:#bcb5d2;line-height:1.6;">
      Выбери направление анализа, загрузи рисунок и получи понятную обратную связь:
      что уже получилось, что можно улучшить и как это сделать.
      </p>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("Выбери своего AI-эксперта")
    st.caption("Один AI-модуль работает в трёх специализированных режимах.")
    columns = st.columns(3, gap="large")
    for column, (mode, info) in zip(columns, MODES.items()):
        with column:
            st.markdown(
                f"""<div class="mode-card">
                <div class="mode-icon">{info['icon']}</div>
                <div class="mode-title">{mode}</div>
                <div class="mode-desc">{info['description']}</div>
                <p style="color:#b6a0f2;font-size:.82rem;font-weight:650;margin-top:.8rem;">
                {info['topics']}</p></div>""",
                unsafe_allow_html=True,
            )
            if st.button(f"Выбрать {mode} →", key=f"mode_{mode}", use_container_width=True):
                open_workspace(mode)
                st.rerun()
    st.markdown(
        '<p class="small-muted" style="text-align:center;margin-top:2rem;">ArtMentor · MVP · AI-помощник для художников</p>',
        unsafe_allow_html=True,
    )

elif st.session_state.page == "workspace":
    mode = st.session_state.selected_mode
    if mode not in MODES:
        st.warning("Сначала выбери направление.")
        if st.button("На главную"):
            open_home()
            st.rerun()
    else:
        st.subheader(f"{MODES[mode]['icon']} {MODE_LABELS[mode]}")
        st.caption(MODES[mode]["description"])
        uploaded = st.file_uploader(
            "Загрузи свой рисунок",
            type=["png", "jpg", "jpeg", "webp"],
            key="artwork_upload",
            help="Для тестирования лучше использовать изображение до 10 МБ.",
        )
        goal = st.text_area(
            "Что особенно хочешь проверить? (необязательно)",
            placeholder="Например: хочу проверить анатомию рук или освещение...",
            height=85,
        )
        if uploaded:
            image_bytes = uploaded.getvalue()
            st.image(image_bytes, caption=uploaded.name, use_container_width=True)
            if len(image_bytes) > 10 * 1024 * 1024:
                st.error("Файл больше 10 МБ. Пожалуйста, выбери изображение поменьше.")
            elif st.button("✨ Проанализировать рисунок", type="primary", use_container_width=True):
                try:
                    with st.spinner("ArtMentor изучает рисунок..."):
                        analysis = analyze_art(image_bytes, uploaded.type, mode, goal)
                        image_path = save_uploaded_image(image_bytes, uploaded.name)
                        record = save_analysis({
                            "mode": mode,
                            "mode_code": {"Realism": "Re", "Character": "Ch", "Composition": "Co"}[mode],
                            "original_filename": uploaded.name,
                            "image_path": image_path,
                            "analysis": analysis,
                            "goal": goal,
                            "conversation": [],
                        })
                    st.session_state.current_record_id = record["id"]
                    st.session_state.page = "result"
                    st.rerun()
                except Exception as error:
                    st.error(f"Не удалось выполнить анализ: {error}")
        else:
            st.info("Сначала загрузи изображение, чтобы запустить анализ.")

elif st.session_state.page == "result":
    record = get_record(st.session_state.current_record_id) if st.session_state.current_record_id else None
    if not record:
        st.warning("Результат не найден. Возможно, история ещё не создана.")
        if st.button("На главную"):
            open_home()
            st.rerun()
    else:
        mode = record.get("mode", "Realism")
        st.subheader(f"Результат · {MODE_LABELS.get(mode, mode)}")
        left, right = st.columns([0.9, 1.3], gap="large")
        with left:
            image_bytes = load_image(record.get("image_path", ""))
            if image_bytes:
                st.image(image_bytes, caption=record.get("original_filename", "Рисунок"), use_container_width=True)
            else:
                st.warning("Файл изображения не найден на диске.")
            st.caption("Дата: " + record.get("created_at", "")[:10])
        with right:
            st.markdown(record.get("analysis", "Анализ отсутствует."))
        st.divider()
        st.subheader("Задать уточняющий вопрос")
        for message in record.get("conversation", []):
            with st.chat_message("user" if message.get("role") == "user" else "assistant"):
                st.write(message.get("text", ""))
        question = st.chat_input("Например: можешь подробнее объяснить этот пункт?")
        if question:
            image_bytes = load_image(record.get("image_path", ""))
            if not image_bytes:
                st.error("Не удалось открыть исходное изображение для продолжения диалога.")
            else:
                try:
                    with st.spinner("ArtMentor формулирует ответ..."):
                        answer = answer_followup(
                            image_bytes=image_bytes,
                            mime_type={
                                ".png": "image/png",
                                ".jpg": "image/jpeg",
                                ".jpeg": "image/jpeg",
                                ".webp": "image/webp",
                            }.get(Path(record.get("image_path", "")).suffix.lower(), "image/png"),
                            mode=mode,
                            analysis=record.get("analysis", ""),
                            conversation=record.get("conversation", []),
                            question=question,
                        )
                    conversation = record.get("conversation", [])
                    conversation.extend([
                        {"role": "user", "text": question},
                        {"role": "assistant", "text": answer},
                    ])
                    update_record(record["id"], conversation=conversation)
                    st.rerun()
                except Exception as error:
                    st.error(f"Не удалось получить ответ: {error}")
        if st.button("← К выбору операторов"):
            open_home()
            st.rerun()

elif st.session_state.page == "history":
    st.subheader("История анализов")
    records = load_data()
    if not records:
        st.info("Здесь пока пусто. Первый анализ появится после загрузки рисунка.")
    else:
        for record in records:
            mode = record.get("mode", "")
            date_text = record.get("created_at", "")[:10]
            title = f"{date_text} · {record.get('mode_code', mode)} · {record.get('original_filename', 'Рисунок')}"
            with st.container(border=True):
                st.write(title)
                preview = (record.get("analysis", "").replace("#", "").replace("\n", " "))[:180]
                st.caption(preview + ("..." if len(preview) >= 180 else ""))
                if st.button("Открыть результат", key=f"open_{record.get('id')}"):
                    st.session_state.current_record_id = record.get("id")
                    st.session_state.page = "result"
                    st.rerun()
