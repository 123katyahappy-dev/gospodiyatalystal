"""
Каркас прототипу — стартовий шаблон
Курс «Інноваційні технології», заняття 9 (модуль «AI Startup Sprint»).

Це клікабельний макет твого майбутнього продукту: усі екрани, кнопки й поля
вже на своїх місцях, а замість AI-функцій поки стоять заглушки.
Твоя задача — замінити TODO власними назвами, екранами й елементами
з «Паспорта проєкту». Справжні функції з'являться на занятті 10.
"""
import streamlit as st

st.set_page_config(page_title="ArtMentor", page_icon="🎨", layout="wide")

st.markdown("""
<style>
.stApp {background: linear-gradient(180deg, #fbfaff 0%, #f3f5ff 100%); color:#292744;}
.main .block-container {max-width:1180px; padding-top:2.5rem; padding-bottom:3rem;}
.brand {font-size:2.7rem; font-weight:800; letter-spacing:-1.5px; color:#292744;}
.tagline {color:#77758f; font-size:1.05rem; margin-bottom:1.8rem;}
.eyebrow {color:#927fc2; text-transform:uppercase; font-size:.75rem; font-weight:750; letter-spacing:2px;}
.intro {background:#ffffffd9; border:1px solid #e9e5f5; border-radius:20px; padding:1.3rem 1.5rem; margin:1rem 0 2rem;}
.intro-title {font-size:1.3rem; font-weight:750; color:#302d4d; margin-bottom:.35rem;}
.intro-text {color:#77758f; line-height:1.6; margin:0;}
.mode-card {min-height:260px; background:#fffffff0; border:1px solid #e8e4f2; border-radius:20px; padding:1.25rem; box-shadow:0 8px 25px #4135690b;}
.mode-icon {font-size:2rem; margin-bottom:.6rem;}
.mode-title {color:#302d4d; font-size:1.25rem; font-weight:800; margin-bottom:.5rem;}
.mode-desc {color:#77758f; font-size:.94rem; line-height:1.55;}
.mode-topics {color:#8a78bd; font-size:.82rem; font-weight:650; margin-top:.9rem;}
div.stButton > button {border-radius:12px; border:1px solid #dcd4ef; background:white; color:#5c4b91; font-weight:700; min-height:2.8rem;}
div.stButton > button:hover {border-color:#a996d8; color:#493778; background:#f5f0ff;}
.footer-note {color:#9692a8; font-size:.82rem; text-align:center; margin-top:2.5rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="eyebrow">YOUR PERSONAL AI ART ASSISTANT</div>', unsafe_allow_html=True)
st.markdown('<div class="brand">🖌️ ArtMentor</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Розвивай свій художній стиль. Розумій свої роботи. Малюй упевненіше.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="intro">
  <div class="intro-title">Твоя творчість — наш спільний проєкт ✨</div>
  <p class="intro-text">Обери напрям аналізу, який відповідає твоїй роботі.
  ArtMentor допоможе розібратися з художніми прийомами, побачити можливі проблеми
  та зрозуміти, над чим можна попрацювати.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### Обери свого AI-експерта")
st.caption("Кожен напрям зосереджується на окремих аспектах малюнка.")

modes = [
    ("Realism", "🖼️", "Для реалістичних малюнків, портретів, натюрмортів і живопису. Аналіз форми, об'єму, кольору та поєднання об'єктів із середовищем.", "Реалізм · Живопис · Світлотінь · Колір"),
    ("Character", "✍️", "Для персонажів у різних стилях, зокрема аніме та манґи. Аналіз анатомії, пропорцій, поз, стилізації й покрасу.", "Анатомія · Пози · Стилізація · Покрас"),
    ("Composition", "🏞️", "Для роботи з фоном і побудовою сцени. Аналіз перспективи, освітлення, глибини простору, композиційного балансу та золотого перетину.", "Перспектива · Світло · Фон · Композиція"),
]

cols = st.columns(3, gap="large")
for col, (name, icon, desc, topics) in zip(cols, modes):
    with col:
        st.markdown(f"""
        <div class="mode-card">
          <div class="mode-icon">{icon}</div>
          <div class="mode-title">{name}</div>
          <div class="mode-desc">{desc}</div>
          <div class="mode-topics">{topics}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Обрати {name} →", key=f"choose_{name}", use_container_width=True):
            st.session_state["selected_mode"] = name

selected = st.session_state.get("selected_mode")
if selected:
    st.divider()
    st.success(f"Обрано напрям: {selected}")
    st.info("Наступним кроком тут з'явиться завантаження малюнка та запуск AI-аналізу. Поки що це лише вибір напряму — справжній аналіз ще не підключено.")
    if st.button("Скасувати вибір", key="clear_selection"):
        del st.session_state["selected_mode"]
        st.rerun()

st.markdown('<div class="footer-note">ArtMentor · AI-Helper for artists · MVP prototype</div>', unsafe_allow_html=True)
