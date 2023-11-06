import streamlit as st
from gpt import perform_function

api = st.secrets['API']

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": 'Hello! How can I assist you today?'}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Send a message"):

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = perform_function(st.session_state.messages, api)

    st.chat_message("assistant").markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
