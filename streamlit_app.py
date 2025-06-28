import streamlit as st
import os
from main import TaskOrchestrator

api_key = os.getenv("GEMINI_API_KEY")

st.title("Agent Calculator")

user_input = st.text_area("Enter your task:")

# Process button
if st.button("Process"):
    orchestrator = TaskOrchestrator(api_key=api_key)
    result = orchestrator.process_task(user_input)
    st.write("Result:")
    st.write(result)
