import streamlit as st
import openai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import base64

valid_image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]

service_account= {
  "type" : st.secrets['firebase']['type'],
  "project_id" : st.secrets['firebase']['project_id'],
  "private_key_id" : st.secrets['firebase']['private_key_id'],
  "private_key" : st.secrets['firebase']['private_key'],
  "client_email" : st.secrets['firebase']['client_email'],
  "client_id" : st.secrets['firebase']['client_id'],
  "auth_uri" : st.secrets['firebase']['auth_uri'],
  "token_uri" : st.secrets['firebase']['token_uri'],
  "auth_provider_x509_cert_url" : st.secrets['firebase']['auth_provider_x509_cert_url'],
  "client_x509_cert_url" : st.secrets['firebase']['client_x509_cert_url'],
  "universe_domain" : st.secrets['firebase']['universe_domain']
}

def perform_function(messages):
    chat = openai.ChatCompletion.create( 
            model="gpt-4-vision-preview", messages=messages)
    reply = chat.choices[0].message.content 
    return reply

if not firebase_admin._apps:
    database_url = st.secrets['DB_URL']

    cred = credentials.Certificate(service_account)
    firebase_admin.initialize_app(cred, {
        'databaseURL': database_url
    })

@st.cache_data(experimental_allow_widgets=True)
def sidebar_chats(chats):
    if not chats: return
    for chat in chats:
        if not chat: continue
        st.sidebar.button(label=database.child('chats').child(chat).get()['title'], on_click=load_chat, args=[chat], use_container_width=True)

def load_chat(chat_name):
    st.session_state.messages = database.child('chats').child(chat_name).child('chat').get()
    st.session_state.chat = database.child('chats').child(chat_name)
    
database = db.reference('/')
sidebar_chats(database.child('chats').get())

openai.api_key = str(st.secrets['API'])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": 'Hello! How can I assist you today?'}]


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

file = st.sidebar.file_uploader('')
if prompt := st.chat_input("Send a message"):

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if file:
        if any(file.name.lower().endswith(ext) for ext in valid_image_extensions):
            file = ({"role": "user", 
                     "content": [{
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(file.read()).decode('utf-8')}"}
                }
            ]
        })
        response = perform_function(st.session_state.messages + [file])
    else: 
        response = perform_function(st.session_state.messages)

    st.chat_message("assistant").markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

    if 'chat' not in st.session_state:
        st.session_state.chat = database.child('chats').push()
        st.session_state.chat.set({"title": perform_function([{"role": "user", "content": f"Generate two worded title for following conversation conversation (without quotes):\n{st.session_state.messages}"}])})

    st.session_state.chat.update({'chat': st.session_state.messages})
