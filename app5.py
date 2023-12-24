from functions5 import check_budget

import openai
import ast
import re
import pandas as pd
import json
import os


# Read the OpenAI Api_key
openai.api_key = open("OpenAI_API_Key.txt", "r").read().strip()

response = []
response = check_budget(response)
print(response)




import json

message = {
    "role": "assistant",
    "content": None,
    "function_call": {
        "name": "get_budget",
        "arguments": "{\n  \"budget_value\": 80000,\n  \"currency_symbol\": \"INR\"\n}"
    }
}

# Extracting budget_value and currency_symbol from the message
arguments = json.loads(message["function_call"]["arguments"])
budget_value = arguments["budget_value"]
currency_symbol = arguments["currency_symbol"]

# Printing the extracted values
print("budget_value:", budget_value)
print("currency_symbol:", currency_symbol)