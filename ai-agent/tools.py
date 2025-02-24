import os
import requests
import json
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

#make a simple API call
#response = requests.get("https://www.learnconline.com")

#Step 1
#Create a tool function to be used
def get_weather(longitude, latitude):
    return [{"type": "text","location":"Mumbai", "temperature":"26.6", "unit":"C"}]

#response = get_weather(0,9)
#print(response[0]["location"], " - ", response[0]["temperature"], response[0]["unit"])

#Step 2
#define the tool
#https://platform.openai.com/docs/guides/function-calling?example=get-weather

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current temperature for a given location along with location and unit.",
        "parameters": {
            "type": "object",
            "properties": {
                "longitude": {
                    "type": "number",
                    "description": "longitude of the location"
                },
                "latitude": {
                    "type": "number",
                    "description": "latitude of the location"
                }
            },
            "required": [
                "latitude", "longitude"
            ],
            "additionalProperties": False
        },
        "strict": True
    }
}]

#Step 3
#While making the API call to the openAI - provide the tool as additional parameter
#AI will decide if the functions provided in the tools needs to be called. If it decides YES, it will provide us
#with the necessary parameters needed to make that function call. It does not direct make the function call.
#look in the response for more information
#the finish reason will tell us why the API finished the execution. If the finish reason is "tool_calls", perform
#additional steps to navigate through list of tools specified in the response and call them as part of next steps.
#Gather the reponse in the messages and make a final call to OpenAI to get the final response

message = [
        {
            "role":"system",
            "content":"You are weather assistant who provides weather information based on the location. You should provide information only related to the weather. For something else, politely respond."
        },
        {
            "role": "user",
            "content": "Where is the current weather of mumbai?",
        }
    ]
completion = client.chat.completions.create(
    messages=message,
    model=model,
    tools=tools
)

#look into the action steps of the model
#Check if the AI wants us to make a call to the tool function
print("\n\nFirst completion dump: \n\n", completion.model_dump())

#https://www.youtube.com/watch?v=bZzyPscbtI8&t=840s

def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args)

if completion.choices[0].finish_reason == "tool_calls":

    print("\n\n Assistant message:\n\n", completion.choices[0].message)
    message.append(completion.choices[0].message) #Append message field from the output with role as assistant

    #the below is done to set context of the entire conversation
    for tool_call in completion.choices[0].message.tool_calls:
        name = tool_call.function.name
        print("\n\nFunction name: ", name)
        args = json.loads(tool_call.function.arguments)
        print("\n\nFunction args: ", args)
        
        #make function call
        result = call_function(name, args)
        message.append(
            {
                "role":"tool",
                "tool_call_id":tool_call.id,
                "content":result
            }
        )

    print("\n\nFinal message: \n\n", message)

    #Now we have the full context that is needed
    #Supply the result and get the final response by calling the model again

    #define the format
    class WeatherResponse(BaseModel):
        temperature: float = Field(description="The temperature in Farenhiet")
        response:str = Field(description="A natural language response to the users question")

    #use client.beta.chat.completions.parse to get structured output
    completion_final = client.beta.chat.completions.parse(
        model=model,
        messages=message,
        tools=tools,
        response_format=WeatherResponse
    )

    print("\n\nFinal output for temperature: ", completion_final.choices[0].message.parsed.temperature)
    print("\nThe final response: ", completion_final.choices[0].message.parsed.response)

#Summary - https://www.youtube.com/watch?v=bZzyPscbtI8&t=1080s
#We need to pass tools available for the AI model.
#AI model will decide if the tools needs to be called.
#If it needs to be called, AI model will provide us with the parameters needed to make the call
#We need to check for that in the response and make the necessary call and create a context message
#append all the messages and make the final call
#Note: By appending the messages, we making use of memory from past conversation