import openai
import ast
import re
import pandas as pd
import json

# Read the OpenAI Api_key
openai.api_key = open("OpenAI_API_Key.txt", "r").read().strip()


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
    
    

response = []
response = check_budget(response)
print(response)

