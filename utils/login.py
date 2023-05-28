import streamlit as st
from utils.st_auth import auth_basic


@auth_basic
def main():
    return True