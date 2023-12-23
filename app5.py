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



