import openai
import ast
import re
import pandas as pd
import json

# Read the OpenAI Api_key
openai.api_key = open("OpenAI_API_Key.txt", "r").read().strip()

# --------------------------------------------------------------
# Ask ChatGPT a Question
# --------------------------------------------------------------

def budget_prompting():
    '''
    Returns a list [{"role": "system", "content": system_message}]
    '''
    
    delimiter = "####"
    example_user_req = {'Budget': '80000 INR'}

    
    system_message = f"""

    You are an intelligent laptop gadget expert and your goal is to find the best laptop for a user.
    You have already gathered the relevant questions and you already understand the user profile by analysing the user's responses.
    You final objective is to also get the budget of the user.
    You want to obtain the following information from the user {'Budget': '80000 INR'}
    The python dictionary looks like this {{'Budget': 'values'}}
    The value for 'budget' should be a numerical value extracted from the user's response. 
    The values currently in the dictionary are only representative values. 
    
    {delimiter}Here are some instructions around the values for the different keys. If you do not follow this, you'll be heavily penalised.
    - The value for 'budget' should be a numerical value extracted from the user's response.
    - 'Budget' value needs to be greater than or equal to 25000 INR. If the user says less than that, please mention that there are no laptops in that range.
    - Do not randomly assign values to any of the keys. The values need to be inferred from the user's response.
    {delimiter}

    To fill the dictionary, you need to have the following chain of thoughts:
    {delimiter} Thought 1: Ask a question to understand the user's budget  \n
    If you have received the budget value, then also check if the currency is clear. 
    If the currency is unclear then ask another question to understand what is the currency.
    You are trying to fill the following values {{'Budget': 'values'}} in the python dictionary by asking the user.
    Answer "Yes" or "No" to indicate if you understand the budget and have the right currency. \n
    If yes, proceed to the next step. Otherwise, rephrase the question to capture the budget and the right currency. \n{delimiter}

    {delimiter}Thought 2: Check if you have correctly updated the values for both the budget and also the right currency in the python dictionary. 
    If you are not confident about the budget value or the currency , ask clarifying questions. {delimiter}

    Follow the above chain of thoughts and only output the final updated python dictionary. \n


    {delimiter} Here is a sample conversation between the user and assistant:
    Assistant:"Thanks for all the information. Could you kindly let me know your budget for the laptop? You can use any currency that you prefer. This will help me find options that fit within your price range while meeting the specified requirements."
    User: "My max budget is 80,000"
    Assistant:"Thanks. Which currency is this?"
    User: "Indian Rupees. 80,000 indian rupeed."
    
    Assistant: "{example_user_req}"
    {delimiter}

    Thank the user for providing all the user requirements. And then ask what the budget for the laptop is of the user. Do not start with Assistant: "
    """
    conversation = [{"role": "system", "content": system_message}]
    return conversation


def get_budget(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
        max_tokens = 300
    )
    return response.choices[0].message["content"]

    


completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[
        {"role": "system", "content": "You are an intelligent laptop assistant. You help with questions around laptop."},
        {"role": "system", "content": "With great questions you have already obtained all the information you need to recommend a laptop."},
        {"role": "system", "content": "That last piece of information you need is the budget of the user."},
        {"role": "user", "content": "What is your budget?"},      
    ],
)

output = completion.choices[0].message.content
print(completion)
print(output)

def check_budget(response):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[{"role": "user", "content": "What is your budget?"}],
        functions=[
            {
                "name": "get_budget",
                "description": "Get the budget from the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "budget_value": {
                            "type": "integer",
                            "description": "The budget of the laptop, e.g. 80,000 INRT",
                        },
                        "currency_symbol": {"type": "string", "enum": ["USD", "INR", "EUR", "GBP", "CAD", "AUD", "JPY", "CNY", "CHF", "SEK", "NZD", 'MYR', "MXN", "SGD", "HKD", "NOK", "KRW", "TRY", "RUB"]},
                    },
                    "required": ["budget_value", 'currency_symbol'],
                },
            }
        ],
        function_call="auto",
    )

    message = response["choices"][0]["message"]
    print(message)

    # Step 2, check if the model wants to call a function
    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        function_args = json.loads(message["function_call"]["arguments"])

        # Step 3, call the function
        # Note: the JSON response from the model may not be valid JSON
        function_response = check_budget(
            budget_value=function_args.get("budget_value"),
            currency_symbol=function_args.get("currency_symbol"),
        )

        # Step 4, send model the info on the function call and function response
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "user", "content": "What is your budget?"},
                message,
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                },
            ],
        )
        print(second_response)
        return second_response





"""

# --------------------------------------------------------------
# Use OpenAI’s Function Calling Feature
# --------------------------------------------------------------


# Define the function descriptions
function_descriptions = [
    {
        "name": "get_budget",
        "description": "Get the budget from the user",
        "parameters": {
            "type": "object",
            "properties": {
                "budget_value": {
                    "type": "integer",
                    "description": "The budget of the laptop, e.g. 80000",
                },
                "currency_symbol": {
                    "type": "string",
                    "enum": ["USD", "INR", "EUR", "GBP", "CAD", "AUD", "JPY", "CNY", "CHF", "SEK", "NZD", "MYR", "MXN", "SGD", "HKD", "NOK", "KRW", "TRY", "RUB"],
                },
            },
        },
        "required": ["budget_value", "currency_symbol"],
    },
]

# Define the user prompt
user_prompt = "What is your budget?"

# Make the API call to OpenAI
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[{"role": "user", "content": user_prompt}],
    functions=function_descriptions,
    function_call="auto",
)

# Extract the assistant's reply from the API response
assistant_reply = completion.choices[0].message["content"]

# Print the assistant's reply
print(assistant_reply)

"""

"""

function_descriptions = [
    {
        "name": "get_budget",
        "description": "Get the budget from the user",
        "parameters": {
            "type": "object",
            "properties": {
                "budget_value": {
                    "type": "integer",
                    "description": "The budget of the laptop, e.g. 80000",
                },
                "currency_symbol": {"type": "string", "enum": ["USD", "INR", "EUR", "GBP", "CAD", "AUD", "JPY", "CNY", "CHF", "SEK", "NZD", 'MYR', "MXN", "SGD", "HKD", "NOK", "KRW", "TRY", "RUB"]},
                },
            },
            "required": ["budget_value", "currency_symbol"],
        },    
]

user_prompt = "What is your budget?"

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[{"role": "user", "content": user_prompt}],
    # Add function calling
    functions=function_descriptions,
    function_call="auto",  # specify the function call
)

# It automatically fills the arguments with correct info based on the prompt
# Note: the function does not exist yet

output = completion.choices[0].message
print(output)
"""