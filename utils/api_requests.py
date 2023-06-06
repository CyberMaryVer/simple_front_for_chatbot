import requests
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from utils.st_constants import API_URL, PUBLIC_URL, REQUEST_ASSISTANT, REQUEST_CHATBOT, REQUEST_STREAM

retry_strategy1 = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)

retry_strategy2 = Retry(
    total=10,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504]
)

retry_strategies = {
    'retry_strategy1': retry_strategy1,
    'retry_strategy2': retry_strategy2
}

http = requests.Session()

# check if API_URL, PUBLIC_URL in env variables
# if not, use default value
API_URL = os.getenv("API_URL", API_URL) or API_URL
PUBLIC_URL = os.getenv("PUBLIC_URL", PUBLIC_URL) or PUBLIC_URL


class SysColors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def healthcheck():
    request_url = API_URL + '/api/healthcheck/healthcheck'
    try:
        response = request_api(request=request_url)
        print(response.decode("utf-8")) if response else print("No response")
        return response.decode("utf-8")
    except Exception as e:
        return f"Error while receiving response from {request_url}: {e}"


def request_api(request, strategy='retry_strategy1', **params):
    adapter = HTTPAdapter(max_retries=retry_strategies[strategy])
    http.mount(request, adapter)

    response = http.get(request, params=params)
    # response = requests.get(request, params=params)

    if response.status_code == 200:
        # Return the binary content of the video file
        return response.content
    else:
        # If the response was unsuccessful, raise an exception with the error message
        print(SysColors.RED, request, SysColors.END)
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")


def improve_user_request(user_input, role="Финансовый консультант"):
    # if user asks how to calculate something, add role to the question
    patterns = ["как рассчитать", "как посчитать", "как найти", "как определить", "расчет", "подсчет", "вычисление",
                "как узнать", "как вычислить", "как подсчитать", "как рассчитывается", "как определяется",
                "как определяются", "как рассчитываются", "как вычисляется", "как подсчитывается", "как найти", ]
    is_calculation = any([pattern in user_input.lower() for pattern in patterns])
    if is_calculation:
        user_input = f"Ты - опытный экономист. Ответь на вопрос, расписав свой ответ по шагам, " \
                     f"если нужно - приведи соответствующие формулыю" \
                     f"\n\nВОПРОС\n {user_input}\n\nОТВЕТ ЭКСПЕРТА\n"
        return user_input

    # if user asks about taxes, add role to the question
    patterns = ["налог", "енп", "ндс", "ндфл", "патент", "налогооблож"]
    is_tax = any([pattern in user_input.lower() for pattern in patterns])
    if is_tax:
        user_input = f"Ты - налоговый консультант. Подробно ответь на вопрос, разбив ответ на подпункты" \
                     f"\n\nВОПРОС\n {user_input}\n\nОТВЕТ ЭКСПЕРТА\n"
        return user_input

    user_input = f"Ты - опытный {role}. Дай полный, точный и развернутый ответ на вопрос." \
                 f"\n\nВОПРОС\n {user_input}\n\nОТВЕТ ЭКСПЕРТА\n"
    return user_input


def create_request_data(user_input, tada_key, topic, enrich_sources):
    data = {
        "user_input": user_input,
        "params": {
            "tada_key": tada_key,
            "topic": topic,
            "enrich_sources": enrich_sources
        }
    }
    return data


def request_api_endpoint(endpoint, data, user_id=0, ):
    request_url = f"{API_URL}{endpoint}{user_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    print(SysColors.CYAN, "Requesting...", request_url, SysColors.END)
    response = requests.post(request_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")


def get_ai_assistant_response(user_input, user_id=0,
                              topic="business",
                              enrich_sources=True,
                              tada_key="12345test",
                              endpoint=REQUEST_ASSISTANT):
    print(SysColors.CYAN, "Requesting...", API_URL + REQUEST_ASSISTANT, SysColors.END)
    print(SysColors.CYAN, "User input:", user_input, SysColors.END)
    role = "" if topic in ["business", "tk"] else topic
    topic = topic if topic in ["business", "tk", "hr"] else "other"
    if topic == "other":
        endpoint = REQUEST_CHATBOT
        user_input = improve_user_request(user_input, role=role)
    data = create_request_data(user_input, tada_key, topic, enrich_sources)
    response = request_api_endpoint(endpoint, data, user_id=user_id)
    return response


def get_ai_assistant_stream(user_input, user_id=0,
                            topic="business",
                            enrich_sources=True,
                            tada_key="12345test",
                            endpoint=REQUEST_STREAM):
    # TODO: fix stream request
    request_url = f"{API_URL}{endpoint}{user_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    print(SysColors.CYAN, "Requesting...", request_url, SysColors.END)
    data = create_request_data(user_input, tada_key, topic, enrich_sources)
    response = requests.post(request_url, headers=headers, data=json.dumps(data), stream=True)
    for line in response.iter_lines():
        print(SysColors.CYAN, "Response:", line, SysColors.END)
        if line:
            yield line


if __name__ == "__main__":
    # Healthcheck
    print(SysColors.GREEN, healthcheck(), SysColors.END)
    # Usage
    import json

    question1 = "Какие услуги предоставляет МТС?"
    question2 = "сколько зарабатывает программист в месяц в саратове?"
    answer = get_ai_assistant_response(user_input=question1, user_id=33)
    answer = json.dumps(answer, indent=4, ensure_ascii=False)
    print(SysColors.GREEN, answer, SysColors.END)
