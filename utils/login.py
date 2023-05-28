import os
import streamlit as st
from utils.st_auth import auth_basic

LOGS = "./logs"
ADMIN = "mary"

@auth_basic
def main():
    is_admin = st.session_state.get("username") == ADMIN
    if is_admin:
        logs = [os.path.join(LOGS, f) for f in os.listdir(LOGS)]
        st.write(logs)
        for log in logs:
            with open(log, "r", encoding="utf-8") as f:
                st.write(f.read())
