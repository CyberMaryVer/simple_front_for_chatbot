import os.path
import json
import streamlit as st
from time import time
from PIL import Image
from utils.st_auth import auth_simple
from utils.api_requests import get_ai_assistant_response
from utils.st_markdown import format_str

EXAMPLES = ["Какие выплаты может получить работник при увольнении?",
            "Как рассчитывается EBITDA?",
            "Какие финансовые показатели бизнеса можно улучшить?",
            "Какие мероприятия для малого и среднего бизнеса проводятся в 2023 году?",]
USER_ICON = "https://nregsmp.org/eService/images/User.png"
CHAT_ICON = "https://raw.githubusercontent.com/CyberMaryVer/ai_assistant/master/images/logo.jpg"
CHAT_HI = Image.open("./img/logo-hi.jpg")
CHAT_BUSINESS = Image.open("./img/logo-business-2.jpg")
CHAT_TK = Image.open("./img/logo-tk.jpg")
CHAT_FINANCE = Image.open("./img/logo-finance-2.jpg")
CHAT_EVENTS = Image.open("./img/logo-events.jpg")


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


def st_create_html_chat(question, answer, sources,
                        user_icon=USER_ICON,
                        chat_icon=CHAT_ICON):
    html = ""
    html += f"<div style='display: flex; flex-direction: row; justify-content: flex-start; align-items: center;'>" \
            f"<img src='{user_icon}' style='width: 80px; height: 80px; border-radius: 50%;'>" \
            f"<div style='display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start;'>" \
            f"<div style='margin: 10px; padding: 10px; border: 2px solid (42, 125, 42); background-color: rgb(42, 125, 42); color: rgb(255, 255, 255); border-radius: 5px;'>" \
            f"{question}" \
            f"</div>" \
            f"</div>" \
            f"</div>"
    html += f"<div style='display: flex; flex-direction: row; justify-content: flex-end; align-items: center;'>" \
            f"<div style='display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-end;'>" \
            f"<div style='margin: 10px; padding: 10px; border: 2px solid (176, 227, 230); background-color: rgb(176, 227, 230); color: rgb(17, 22, 23); border-radius: 5px;'>" \
            f"{answer}" \
            f"</div>" \
            f"</div>" \
            f"<img src='{chat_icon}' style='width: 80px; height: 80px; border-radius: 10%;'>" \
            f"</div>" \
            f"<hr>"
    sources_html = ""
    for source in sources:
        sources_html += f"<a href='{source}' target='_blank'>{source}</a><br>"
    html += f"<div style='display: flex; flex-direction: row; justify-content: flex-end; align-items: center;'>" \
            f"<div style='display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-end;'>" \
            f"<div style='margin: 10px;'>" \
            f"{sources_html}" \
            f"</div>" \
            f"</div>" \
            f"</div>"
    return html


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
            "Ивент-менеджер",
            # "Специалист по кадрам",
            # "Специалист по маркетингу",
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
        elif chat_role == "Ивент-менеджер":
            topic = chat_role
            with chat_img:
                st.image(CHAT_EVENTS, width=200)
        else:
            topic = chat_role

        if st.checkbox("Показать примеры вопросов"):
            st.write(EXAMPLES)
        if st.checkbox("Обновить ключ"):
            st_key_update()

    with col1:
        with st.form("my_form"):
            st.markdown("❓**Введите свой вопрос**")
            example_input = EXAMPLES[0]
            instructions = f"* Пример вопроса по тематике ТК: {EXAMPLES[0]}\n" \
                            f"* Пример вопроса по тематике Бизнес: {EXAMPLES[1]}\n" \
                            f"* Пример вопроса по тематике Финансы: {EXAMPLES[2]}\n" \
                            f"* Пример вопроса по тематике Ивенты: {EXAMPLES[3]}\n"
            st.markdown(instructions)
            user_input = st.text_area("question", height=100, max_chars=500, placeholder=example_input,
                                      label_visibility="collapsed")
            tada_key = st.session_state.get("tada_key") or "54321test"

            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                # st.markdown(f"###### Вы отправили вопрос :green[{user_input}]")

                with st.spinner("Подождите, идет обработка запроса..."):
                    answer = get_ai_assistant_response(user_input=user_input,
                                                       user_id="demo",
                                                       topic=topic,
                                                       tada_key=tada_key)

                html = st_create_html_chat(question=user_input,
                                           answer=answer.get("answer"),
                                           sources=answer.get("sources"))
                st.markdown(html, unsafe_allow_html=True)

                st_format_ai_answer(answer)


if __name__ == "__main__":
    main(admin=False)
