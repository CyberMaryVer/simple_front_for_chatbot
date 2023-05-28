USER_ICON = "https://nregsmp.org/eService/images/User.png"
CHAT_ICON = "https://raw.githubusercontent.com/CyberMaryVer/ai_assistant/master/images/logo.jpg"
INFO_ICON = "https://cdn-icons-png.flaticon.com/512/813/813776.png"


def st_create_html_chat(question, answer, sources,
                        user_icon=USER_ICON,
                        chat_icon=CHAT_ICON,
                        info_icon=INFO_ICON):
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
            f"<div style='margin: 10px; padding: 10px; border: 2px solid (176, 227, 230); background-color: rgb(176, 227, 230); color: rgb(0, 0, 0); border-radius: 5px;'>" \
            f"{answer}" \
            f"</div>" \
            f"</div>" \
            f"<img src='{chat_icon}' style='width: 60px; height: 80px; border-radius: 10%;'>" \
            f"</div>" \
            f"<hr>"
    sources_html = ""

    try:
        if type(sources) == dict:
            for source_key in sources.keys():
                source_href, source_text = sources[source_key]['href'], sources[source_key]['name']
                sources_html += f"<a href='{source_href}' target='_blank'>{source_text}</a><br>"
        else:
            for source in sources:
                source_href = source
                source_text = source
                if len(source_text) > 50:
                    source_text = source_text[:50] + "..."
                sources_html += f"<a href='{source_href}' target='_blank'>{source_text}</a><br>"
        html += f"<div style='display: flex; flex-direction: row; justify-content: flex-end; align-items: center;'>" \
                f"<img src='{info_icon}' style='width: 80px; height: 80px;'>" \
                f"<div style='display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-end;'>" \
                f"<div style='margin: 10px;'>" \
                f"{sources_html}" \
                f"</div>" \
                f"</div>" \
                f"</div>"
    except Exception as e:
        print(f"[{__name__}] Error decoding: {e}")
        html += f"<div style='display: flex; flex-direction: row; justify-content: flex-end; align-items: center;'>" \
                f"<img src='{info_icon}' style='width: 80px; height: 80px;'>" \
                f"<div style='display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-end;'>" \
                f"<div style='margin: 10px;'>" \
                f"Не удалось отобразить источники информации" \
                f"</div>" \
                f"</div>" \
                f"</div>"
    return html
