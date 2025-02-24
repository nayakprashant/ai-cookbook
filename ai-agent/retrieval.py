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

#Step 1
#Create a tool function to return the knowledge base json file
def search_kb(question: str):
    with open("kb.json", "r") as f:
        return json.load(f)

#Step 2
#define the tool
#https://platform.openai.com/docs/guides/function-calling?example=get-weather

tools = [{
    "type": "function",
    "function": {
        "name": "search_kb",
        "description": "This function accepts question for a product as a string parameter and returns the question and answer from the knowledge base json file.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "question about the product"
                }
            },
            "required": [
                "question"
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
            "content":"You are a customer service representative who answers questions related to the product. \
                Rephrase the answers you get from knowledge base to make it more natural. You should provide information only related to the product. For something else, politely respond."
        },
        {
            "role": "user",
            "content": "what is the warranty terms?",
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
    if name == "search_kb":
        return search_kb(**args)

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
                "content":json.dumps(result) #convert to json format
            }
        )

    print("\n\nFinal message: \n\n", message)

    #Now we have the full context that is needed
    #Supply the result and get the final response by calling the model again

    #define the format
    class SupportResponse(BaseModel):
        response:str = Field(description="A natural language response to the users question on the product")

    #use client.beta.chat.completions.parse to get structured output
    completion_final = client.beta.chat.completions.parse(
        model=model,
        messages=message,
        tools=tools,
        response_format=SupportResponse
    )

    print("\nThe final response: ", completion_final.choices[0].message.parsed.response)

#Summary - https://www.youtube.com/watch?v=bZzyPscbtI8&t=1080s
#We need to pass tools available for the AI model.
#AI model will decide if the tools needs to be called.
#If it needs to be called, AI model will provide us with the parameters needed to make the call
#We need to check for that in the response and make the necessary call and create a context message
#append all the messages and make the final call
#Note: By appending the messages, we making use of memory from past conversation