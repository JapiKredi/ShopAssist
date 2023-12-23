import openai
import ast
import re
import pandas as pd
import json

# Read the OpenAI Api_key
openai.api_key = open("OpenAI_API_Key.txt", "r").read().strip()



# --------------------------------------------------------------
# Use OpenAI’s Function Calling Feature
# --------------------------------------------------------------

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

user_prompt = "WEhat is your budget?"

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












