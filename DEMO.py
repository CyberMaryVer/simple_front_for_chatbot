import json
import os
import csv
import streamlit as st

from utils.api_requests import get_ai_assistant_response, get_ai_assistant_stream
from utils.html_chat import st_create_html_chat, st_create_html_info
from utils.metadata import CHAT_HI, CHAT_BUSINESS, CHAT_TK, CHAT_FINANCE, CHAT_EVENTS, LOGS, \
    EXAMPLES_TK, EXAMPLES_B, EXAMPLES_C, EXAMPLES_F, \
    DESCRIPTION_BUSINESS, DESCRIPTION_TK, DESCRIPTION_FINANCE, DESCRIPTION_HR


def _log_user_question(user_input, user_key, topic="default"):
    os.makedirs(LOGS, exist_ok=True)
    # create csv file with header if not exists
    if not os.path.exists(f"{LOGS}/user_questions_{user_key}.csv"):
        with open(f"{LOGS}/user_questions_{user_key}.csv", "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["user_input", "topic"])
    with open(f"{LOGS}/user_questions_{user_key}.csv", "a", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([user_input, topic])


def _log_ai_answer(answer, user_key):
    os.makedirs(LOGS, exist_ok=True)
    # create csv file with header if not exists
    if not os.path.exists(f"{LOGS}/ai_answers_{user_key}.csv"):
        with open(f"{LOGS}/ai_answers_{user_key}.csv", "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["question", "answer", "sources", "topic", "elapsed_time", "uses_left"])
    with open(f"{LOGS}/ai_answers_{user_key}.csv", "a", encoding="utf-8") as f:
        writer = csv.writer(f)

        try:
            user_request = answer["user_request"] or {}
            writer.writerow([user_request.get("user_input"), answer.get("answer"), answer.get("sources"),
                             user_request.get("topic"), answer.get("elapsed_time"), answer.get("uses_left")])
        except Exception as e:
            with open(f"{LOGS}/errors.csv", "a", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([answer, e])


def st_key_update():
    """
    This function updates user key
    """
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

    uses_left = answer.get("uses_left") or answer.get("key_status")
    st.write(f"Время ответа: {answer.get('elapsed_time'):.2f} сек.")
    st.write(f"Осталось запросов: {uses_left}")


def st_format_info(img_placeholder, info_placeholder, img, description):
    """
    This function formats info for streamlit
    """
    desc, info = description.split("----")
    html = st_create_html_info(info)
    with img_placeholder:
        st.image(img, width=150)
    with info_placeholder:
        st.markdown(html, unsafe_allow_html=True)
    with st.expander("Подробнее", expanded=True):
        desc1, desc2 = desc.split("--")
        html_desc1 = st_create_html_info(desc1, info_color="#ffffff", info_icon="📌", break_line=False)
        html_desc2 = st_create_html_info(desc2, info_color="#ffffff", info_icon="📌", break_line=False)
        st.markdown(html_desc1, unsafe_allow_html=True)
        st.markdown(html_desc2, unsafe_allow_html=True)


def main(admin=None):
    """
    This function is a main program function
    :return: None
    """

    col1, col2 = st.columns([5, 2])
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
        chat_info = st.empty()
        if chat_role == "Бизнес-консультант":
            topic = "business+hr"
            st_format_info(chat_img, chat_info, CHAT_BUSINESS, DESCRIPTION_BUSINESS)
        elif chat_role == "Специалист по ТК":
            topic = "tk"
            st_format_info(chat_img, chat_info, CHAT_TK, DESCRIPTION_TK)
        elif chat_role == "Финансовый консультант":
            topic = chat_role
            st_format_info(chat_img, chat_info, CHAT_FINANCE, DESCRIPTION_FINANCE)
        elif chat_role == "Помощник руководителя":
            topic = "yt"
            st_format_info(chat_img, chat_info, CHAT_EVENTS, DESCRIPTION_HR)
        else:
            topic = chat_role
        st.markdown("----")
        if st.checkbox("Обновить ключ"):
            st_key_update()

    with col1:
        with st.form("my_form"):
            st.markdown("❓**Введите свой вопрос**")
            examples = EXAMPLES_TK if topic == "tk" else EXAMPLES_B if topic == "business+hr" else \
                EXAMPLES_C if topic == "yt" else EXAMPLES_F
            example_input = examples[0] if topic == "tk" else examples[1] if topic == "business+hr" else \
                examples[3] if topic == "yt" else examples[2]
            instructions = f"* Пример вопроса по тематике: {examples[0]}\n" \
                           f"* Пример вопроса по тематике: {examples[1]}\n" \
                           f"* Пример вопроса по тематике: {examples[3]}\n" \
                           f"* Пример вопроса по тематике: {examples[2]}\n"
            st.markdown(instructions)
            user_input = st.text_area("question", height=100, max_chars=500, placeholder=example_input,
                                      label_visibility="collapsed")
            tada_key = st.session_state.get("tada_key") or "12345test"

            # Enrich sources and enhance text for TK, YouTube
            enrich_sources = True if topic == "tk" else False
            enhance_text = True if topic == "yt" else False

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
                                               sources=answer.get("sources"),
                                               enhance_text=enhance_text)
                    st.markdown(html, unsafe_allow_html=True)

                    st_format_ai_answer(answer)

                except Exception as e:
                    st.info("Произошла ошибка. Проверьте ваш ключ и попробуйте еще раз.")
                    _log_ai_answer(answer={"answer": str(e)}, user_key=tada_key)


if __name__ == "__main__":
    main(admin=False)
