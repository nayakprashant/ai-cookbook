import os
from openai import OpenAI
from dotenv import load_dotenv

from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
api_key = os.getenv("OPENAI_API_KEY")

#Get the model to be used
model = os.getenv("CHAT_GPT_MODEL")

client = OpenAI(
    api_key=api_key
)

#define the structure format
class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]
    agenda: str = Field(description="Detailed description of the event")

#use client.beta.chat.completions.parse to get structured output
completion = client.beta.chat.completions.parse(
    model=model,
    messages=[
        {
            "role":"system",
            "content":"Extract the event information"
        },
        {
            "role":"user",
            "content":"Alice and Bob are going to science fair on Friday"
        }
    ],
    response_format=CalendarEvent
)

event = completion.choices[0].message.parsed
print(event)