
im = "question"
DARK_THEME = False
DEBUG_MODE = False
PAGE_CONFIG = dict(page_title="ai-assistant-demo",
                   page_icon=im,
                   layout="wide",
                   menu_items={
                       'Get Help': 'https://chat.openai.com/chat',
                       'About': "![img]()"
                   })
# API_URL = "http://localhost:8000"
API_URL = "http://178.170.196.101:8080"
PUBLIC_URL = "http://localhost:8000"
REQUEST_ASSISTANT = "/api/chatbot_topic/"
REQUEST_CHATBOT = "/api/chatbot_simple/"
REQUEST_STREAM = "/api/chatbot_stream/"

