import openai

def perform_function(messages, api):
    openai.api_key = api
    chat = openai.ChatCompletion.create( 
            model="gpt-4", messages=messages)
    reply = chat.choices[0].message.content 

    return reply