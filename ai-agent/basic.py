import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
api_key = os.getenv("OPENAI_API_KEY")

#Get the model to be used
model = os.getenv("CHAT_GPT_MODEL")

client = OpenAI(
    api_key=api_key
)

#we use client.chat.completions.create to get text back from the model api
completion = client.chat.completions.create(
    messages=[
        {
            "role":"system",
            "content":"You are helpful assistant"
        },
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model=model,
)

response =  completion.choices[0].message.content
print(response)