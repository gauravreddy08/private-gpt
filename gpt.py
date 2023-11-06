import openai

openai.api_key = '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'

def perform_function(messages):
    chat = openai.ChatCompletion.create( 
            model="gpt-4", messages=messages)
    reply = chat.choices[0].message.content 

    return reply





