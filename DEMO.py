import os

import streamlit as st
from time import time
from PIL import Image
from utils.api_requests import get_ai_assistant_response
from utils.html_chat import st_create_html_chat

EXAMPLES = ["Какие выплаты может получить работник при увольнении?",
            "Как получить кредит для бизнеса в Москве?",
            "Как рассчитывается EBITDA?",
            "Какие мероприятия для малого и среднего бизнеса проводятся в 2023 году?", ]

CHAT_HI = Image.open("./img/logo-hi.jpg")
CHAT_BUSINESS = Image.open("./img/logo-business-2.jpg")
CHAT_TK = Image.open("./img/logo-tk-2.jpg")
CHAT_FINANCE = Image.open("./img/logo-finance-2.jpg")
CHAT_EVENTS = Image.open("./img/logo-events.jpg")
LOGS = "./logs"


def _log_user_question(user_input, user_key, topic="default"):
    os.makedirs(LOGS, exist_ok=True)
    with open(f"{LOGS}/user_questions_{user_key}.txt", "a", encoding="utf-8") as f:
        f.write(f"USER_INPUT: {user_input}, TOPIC: {topic}\n")


def _log_ai_answer(answer, user_key):
    os.makedirs(LOGS, exist_ok=True)
    with open(f"{LOGS}/ai_answers_{user_key}.txt", "a", encoding="utf-8") as f:
        f.write(f"{answer}\n")


def st_key_update():
    with st.expander("Обновить ключ"):
        with st.form("key_form"):
            st.markdown("❓**Введите свой ключ**")
            example_input = "Введите ключ"
            user_input = st.text_area("key-xxxx", height=50, max_chars=500, placeholder=example_input,
                                      label_visibility="collapsed")
            submitted = st.form_submit_button("Сохранить")
            if submitted:
                st.session_state["tada_key"] = user_input


def st_format_ai_answer(answer):
    """
    This function formats AI assistant response for streamlit
    """
    with st.expander("Показать полный ответ API"):
        st.write(answer)
    if answer.get("error"):
        st.error(answer.get("error"))
        return

    st.write(f"Время ответа: {answer.get('elapsed_time'):.2f} сек.")
    st.write(f"Осталось запросов: {answer.get('uses_left')}")


def main(admin=None):
    """
    This function is a main program function
    :return: None
    """

    col1, col2 = st.columns([3, 1])
    with col2:
        chat_img = st.empty()
        with chat_img:
            st.image(CHAT_BUSINESS, width=200)
        chat_role = st.selectbox("Выберите собеседника", [
            "Бизнес-консультант",
            "Специалист по ТК",
            "Помощник руководителя",
            "Финансовый консультант",
        ])
        if chat_role == "Бизнес-консультант":
            topic = "business"
            with chat_img:
                st.image(CHAT_BUSINESS, width=200)
        elif chat_role == "Специалист по ТК":
            topic = "tk"
            with chat_img:
                st.image(CHAT_TK, width=200)
        elif chat_role == "Финансовый консультант":
            topic = chat_role
            with chat_img:
                st.image(CHAT_FINANCE, width=200)
        elif chat_role == "Помощник руководителя":
            topic = "hr"
            with chat_img:
                st.image(CHAT_EVENTS, width=200)
        else:
            topic = chat_role
        st.markdown("----")
        if st.checkbox("Обновить ключ"):
            st_key_update()

    with col1:
        with st.form("my_form"):
            st.markdown("❓**Введите свой вопрос**")
            example_input = EXAMPLES[0]
            instructions = f"* Пример вопроса по тематике ТК: {EXAMPLES[0]}\n" \
                           f"* Пример вопроса по тематике Бизнес: {EXAMPLES[1]}\n" \
                           f"* Пример вопроса по тематике Финансы: {EXAMPLES[2]}\n" \
                           f"* Пример вопроса по тематике Управление: {EXAMPLES[3]}\n"
            st.markdown(instructions)
            user_input = st.text_area("question", height=100, max_chars=500, placeholder=example_input,
                                      label_visibility="collapsed")
            tada_key = st.session_state.get("tada_key") or "12345test"
            enrich_sources = True if topic == "tk" else False

            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                _log_user_question(user_input=user_input, user_key=tada_key, topic=topic)

                try:
                    with st.spinner("Подождите, идет обработка запроса..."):
                        answer = get_ai_assistant_response(user_input=user_input,
                                                           user_id="demo",
                                                           topic=topic,
                                                           tada_key=tada_key,
                                                           enrich_sources=enrich_sources)
                        _log_ai_answer(answer=answer, user_key=tada_key)
                    print(answer.get("sources"))
                    html = st_create_html_chat(question=user_input,
                                               answer=answer.get("answer"),
                                               sources=answer.get("sources"))
                    st.markdown(html, unsafe_allow_html=True)

                    st_format_ai_answer(answer)

                except Exception as e:
                    st.info("Произошла ошибка. Проверьте ваш ключ и попробуйте еще раз.")
                    _log_ai_answer(answer={"answer": str(e)}, user_key=tada_key)


if __name__ == "__main__":
    main(admin=False)
