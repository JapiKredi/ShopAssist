import openai
import ast
import re
import pandas as pd
import json
import requests

def initialize_conversation():
    '''
    Returns a list [{"role": "system", "content": system_message}]
    '''
    
    delimiter = "####"
    example_user_req = {'GPU intensity': 'high','Display quality': 'high','Portability': 'low','Multitasking': 'high','Processing speed': 'high','Budget': '150000'}
    
    system_message = f"""

    You are an intelligent laptop gadget expert and your goal is to find the best laptop for a user.
    You need to ask relevant questions and understand the user profile by analysing the user's responses.
    You final objective is to fill the values for the different keys ('GPU intensity','Display quality','Portability','Multitasking','Processing speed','Budget') in the python dictionary and be confident of the values.
    These key value pairs define the user's profile.
    The python dictionary looks like this {{'GPU intensity': 'values','Display quality': 'values','Portability': 'values','Multitasking': 'values','Processing speed': 'values','Budget': 'values'}}
    The values for all keys, except 'budget', should be 'low', 'medium', or 'high' based on the importance of the corresponding keys, as stated by user. 
    The value for 'budget' should be a numerical value and also the currency extracted from the user's response.It can be Indian Rupees, Euros, Dollars, or any currency.
    Please note down tje currency symbol such as INR for indian rupees, USD for dollars, EUR for euros, etc. 
    The values currently in the dictionary are only representative values. 
    
    {delimiter}Here are some instructions around the values for the different keys. If you do not follow this, you'll be heavily penalised.
    - The values for all keys, except 'Budget', should strictly be either 'low', 'medium', or 'high' based on the importance of the corresponding keys, as stated by user.
    - The value for 'budget' should be a numerical value and the currency extracted from the user's response. The user can chose any currency. 
    - Do not randomly assign values to any of the keys. The values need to be inferred from the user's response.
    {delimiter}

    To fill the dictionary, you need to have the following chain of thoughts:
    {delimiter} Thought 1: Ask a question to understand the user's profile and requirements. \n
    If their primary use for the laptop is unclear. Ask another question to comprehend their needs.
    You are trying to fill the values of all the keys ('GPU intensity','Display quality','Portability','Multitasking','Processing speed','Budget') in the python dictionary by understanding the user requirements.
    Identify the keys for which you can fill the values confidently using the understanding. \n
    Remember the instructions around the values for the different keys. 
    Answer "Yes" or "No" to indicate if you understand the requirements and have updated the values for the relevant keys. \n
    If yes, proceed to the next step. Otherwise, rephrase the question to capture their profile. \n{delimiter}

    {delimiter}Thought 2: Now, you are trying to fill the values for the rest of the keys which you couldn't in the previous step. 
    Remember the instructions around the values for the different keys. Ask questions you might have for all the keys to strengthen your understanding of the user's profile.
    Answer "Yes" or "No" to indicate if you understood all the values for the keys and are confident about the same. 
    If yes, move to the next Thought. If no, ask question on the keys whose values you are unsure of. \n
    It is a good practice to ask question with a sound logic as opposed to directly citing the key you want to understand value for.{delimiter}

    {delimiter}Thought 3: Check if you have correctly updated the values for the different keys in the python dictionary. 
    If you are not confident about any of the values, ask clarifying questions. {delimiter}

    Follow the above chain of thoughts and only output the final updated python dictionary. \n


    {delimiter} Here is a sample conversation between the user and assistant:
    User: "Hi, I am an editor."
    Assistant: "Great! As an editor, you likely require a laptop that can handle demanding tasks. Hence, the laptop should have high multitasking capability. You would also need a high end display for better visuals and editing. May I know what kind of work do you primarily focus on? Are you more involved in video editing, photo editing, or both? Understanding the specific type of editing work will help me tailor my recommendations accordingly. Let me know if my understanding is correct until now."
    User: "I primarily work with After Effects."
    Assistant: "Thank you for providing that information. Working with After Effects involves working with graphics, animations, and rendering, which will require high GPU. Do you work with high-resolution media files, such as 4K videos or RAW photos? Understanding your file sizes will help determine the storage capacity and processing power needed."
    User: "Yes, sometimes I work with 4K videos as well."
    Assistant: "Thank you for the information. Processing 4K vidoes will require a good processor and high GPU. I think we have already determined earlier that you need a high GPU. To ensure I have a complete understanding of your needs, I have one more question: Are you frequently on the go and require a laptop that is lightweight and easy to carry, or do you primarily work from a stationary location?"
    User: "Yes, sometimes I travel but do not carry my laptop."
    Assistant:"Could you kindly let me know your budget for the laptop? You can choose any currency you wish. This will help me find options that fit within your price range while meeting the specified requirements."
    User: "My max budget is 80,000"
    Assistant:"Which currency is this?"
    User: "My max budget is 80,000 Malaysianm Ringgit"
    Assistant:"Which currency code is that?"
    User: "80,000 MYR"
    
    Assistant: "{example_user_req}"
    {delimiter}

    Start with a short welcome message and encourage the user to share their requirements. Do not start with Assistant: "
    """
    conversation = [{"role": "system", "content": system_message}]
    return conversation



def get_chat_model_completions(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
        max_tokens = 300
    )
    return response.choices[0].message["content"]



def moderation_check(user_input):
    response = openai.Moderation.create(input=user_input)
    moderation_output = response["results"][0]
    if moderation_output["flagged"] == True:
        return "Flagged"
    else:
        return "Not Flagged"


    
def intent_confirmation_layer(response_assistant):
    delimiter = "####"
    prompt = f"""
    You are a senior evaluator who has an eye for detail.
    You are provided an input. You need to evaluate if the input has the following keys: 'GPU intensity','Display quality','Portability','Multitasking',' Processing speed','Budget'
    Next you need to evaluate if the keys have the the values filled correctly.
    The values for all keys, except 'budget', should be 'low', 'medium', or 'high' based on the importance as stated by user. 
    The value for the key 'budget' needs to contain a number with the currency. The currency can be any currency. 
    Output a string 'Yes' if the input contains the dictionary with the values correctly filled for all keys.
    Otherwise out the string 'No'.

    Here is the input: {response_assistant}
    Only output a one-word string - Yes/No.
    """


    confirmation = openai.Completion.create(
                                    model="text-davinci-003",
                                    prompt = prompt,
                                    temperature=0)


    return confirmation["choices"][0]["text"]




def dictionary_present(response):
    delimiter = "####"
    user_req = {'GPU intensity': 'high','Display quality': 'high','Portability': 'medium','Multitasking': 'high','Processing speed': 'high','Budget': '200000 INR'}
    prompt = f"""You are a python expert. You are provided an input.
            You have to check if there is a python dictionary present in the string.
            It will have the following format {user_req}.
            Your task is to just extract and return only the python dictionary from the input.
            The output should match the format as {user_req}.
            The output should contain the exact keys and values as present in the input.

            Here are some sample input output pairs for better understanding:
            {delimiter}
            input: - GPU intensity: low - Display quality: high - Portability: low - Multitasking: high - Processing speed: medium - Budget: 50,000 INR
            output: {{'GPU intensity': 'low', 'Display quality': 'high', 'Portability': 'low', 'Multitasking': 'high', 'Processing speed': 'medium', 'Budget': '50000'}}

            input: {{'GPU intensity':     'low', 'Display quality':     'high', 'Portability':    'low', 'Multitasking': 'high', 'Processing speed': 'medium', 'Budget': '90,000'}}
            output: {{'GPU intensity': 'low', 'Display quality': 'high', 'Portability': 'low', 'Multitasking': 'high', 'Processing speed': 'medium', 'Budget': '90000'}}

            input: Here is your user profile 'GPU intensity': 'high','Display quality': 'high','Portability': 'medium','Multitasking': 'low','Processing speed': 'high','Budget': '200000 INR'
            output: {{'GPU intensity': 'high','Display quality': 'high','Portability': 'medium','Multitasking': 'high','Processing speed': 'low','Budget': '200000'}}
            {delimiter}

            Here is the input {response}

            """
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens = 2000
        # temperature=0.3,
        # top_p=0.4
    )
    return response["choices"][0]["text"]



def extract_dictionary_from_string(string):
    regex_pattern = r"\{[^{}]+\}"

    dictionary_matches = re.findall(regex_pattern, string)

    # Extract the first dictionary match and convert it to lowercase
    if dictionary_matches:
        dictionary_string = dictionary_matches[0]
        dictionary_string = dictionary_string.lower()

        # Convert the dictionary string to a dictionary object using ast.literal_eval()
        dictionary = ast.literal_eval(dictionary_string)
    return dictionary

"""
def get_budget(conversation):
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=conversation, #[{"role": "assistant", "content": "What is your budget for the laptop?"}],
        functions=[
            {
                "name": "get_budget",
                "description": "Get the budget of the laptop from the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "budget_value": {
                            "type": "string",
                            "description": "The budget of the laptop, e.g. 80,000",
                        },
                        "currency_symbol": {"type": "string", "enum": ["USD", "INR", "EUR", "GBP", "CAD", "AUD", "JPY", "CNY", "CHF", "SEK", "NZD", 'MYR', "MXN", "SGD", "HKD", "NOK", "KRW", "TRY", "RUB"]},
                    },
                    "required": ["budget_value", 'currency_symbol'],
                },
            }
        ],
        function_call="auto",
    )

    return response.choices[0].message["content"]
""" 
"""
def get_budget(conversation_bot):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        messages=conversation_bot,
        functions=[
            {
                "name": "get_budget",
                "description": "Get the budget of the laptop from the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "budget_value": {
                            "type": "string",
                            "description": "The budget of the laptop, e.g. 80,000",
                        },
                        "currency_symbol": {"type": "string", "enum": ["USD", "INR", "EUR", "GBP", "CAD", "AUD", "JPY", "CNY", "CHF", "SEK", "NZD", 'MYR', "MXN", "SGD", "HKD", "NOK", "KRW", "TRY", "RUB"]},
                    },
                    "required": ["budget_value", 'currency_symbol'],
                },
            }
        ],
        function_call="auto",
    )
    print('Printing the response output of get_budget function')
    print(response)
    return response
    #return response.choices[0].message["content"]["budget_value"], #response.choices[0].message["content"]["currency_symbol"]
"""

def get_budget(conversation_bot):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        messages=conversation_bot,
        functions=[
            {
                "name": "get_budget",
                "description": "Get the budget of the laptop from the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "budget_value": {
                            "type": "string",
                            "description": "The budget of the laptop, e.g. 80,000",
                        },
                        "currency_symbol": {"type": "string", "enum": ["USD", "INR", "EUR", "GBP", "CAD", "AUD", "JPY", "CNY", "CHF", "SEK", "NZD", 'MYR', "MXN", "SGD", "HKD", "NOK", "KRW", "TRY", "RUB"]},
                    },
                    "required": ["budget_value", 'currency_symbol'],
                },
            }
        ],
        function_call="auto",
    )
    print('Printing the response output of get_budget function')
    print(response)
    
    # Extracting the budget_value and currency_symbol from the response
    function_call = response['choices'][0]['message']['function_call']
    arguments = json.loads(function_call['arguments'])
    budget_value = arguments['budget_value']
    currency_symbol = arguments['currency_symbol']
    
    return budget_value, currency_symbol


def get_currency_value(currency_symbol):
    API_KEY = open("API_Key.txt", "r").read().strip()
    url = f"http://api.exchangeratesapi.io/latest?access_key={API_KEY}"
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        print("Status Code:", response.status_code)
        raise Exception("There was an error!")

    data = response.json()

    # Check if the currency symbols exist in the rates dictionary
    if 'INR' in data['rates'] and currency_symbol in data['rates']:
        inr_value = data['rates']['INR']
        currency_value = data['rates'][currency_symbol]
        return inr_value, currency_value
    else:
        raise ValueError("Invalid currency symbol")

# Example usage
#def main():
#    currency_symbol = 'USD'
#    inr_value, currency_value = get_currency_value(currency_symbol)
#    print(f"The value of INR is: {inr_value}")
#    print(f"The value of {currency_symbol} is: {currency_value}")


def compare_laptops_with_user(user_req_string, currency_conversion_rate, currency_symbol):
    laptop_df= pd.read_csv('updated_laptop.csv')
    user_requirements = extract_dictionary_from_string(user_req_string)
    print(currency_conversion_rate)
    budget = int(user_requirements.get('budget', '0').replace(',', '').split()[0])
    
    #This line retrieves the value associated with the key 'budget' from the user_requirements dictionary.
    #If the key is not found, the default value '0' is used.
    #The value is then processed to remove commas, split it into a list of strings, and take the first element of the list.
    #Finally, the resulting value is converted to an integer and assigned to the variable budget.


    filtered_laptops = laptop_df.copy()
    filtered_laptops['Price'] = filtered_laptops['Price'].str.replace(',','').astype(int)
    filtered_laptops['Price'] = filtered_laptops['Price'] * currency_conversion_rate
    filtered_laptops['Currency'] = currency_symbol
    filtered_laptops = filtered_laptops[filtered_laptops['Price'] <= budget].copy()
    print(filtered_laptops[['Brand', 'Model Name', 'Price', 'Currency']])

    #These lines create a copy of the laptop_df DataFrame and assign it to filtered_laptops.
    #They then modify the 'Price' column in filtered_laptops by removing commas and converting the values to integers.
    #Finally, they filter filtered_laptops to include only rows where the 'Price' is less than or equal to the budget.

    mappings = {
        'low': 0,
        'medium': 1,
        'high': 2
    }
    # Create 'Score' column in the DataFrame and initialize to 0
    filtered_laptops['Score'] = 0
    for index, row in filtered_laptops.iterrows():
        user_product_match_str = row['laptop_feature']
        laptop_values = extract_dictionary_from_string(user_product_match_str)
        score = 0

        for key, user_value in user_requirements.items():
            if key.lower() == 'budget':
                continue  # Skip budget comparison
            laptop_value = laptop_values.get(key, None)
            laptop_mapping = mappings.get(laptop_value.lower(), -1)
            user_mapping = mappings.get(user_value.lower(), -1)
            if laptop_mapping >= user_mapping:
                ### If the laptop value is greater than or equal to the user value the score is incremented by 1
                score += 1

        filtered_laptops.loc[index, 'Score'] = score

    # Sort the laptops by score in descending order and return the top 5 products
    top_laptops = filtered_laptops.drop('laptop_feature', axis=1)
    top_laptops = top_laptops.sort_values('Score', ascending=False).head(3)
    #print(top_laptops.head())
    return top_laptops.to_json(orient='records')


def recommendation_validation(laptop_recommendation):
    data = json.loads(laptop_recommendation)
    data1 = []
    for i in range(len(data)):
        if data[i]['Score'] > 2:
            data1.append(data[i])

    return data1




def initialize_conv_reco(products, currency_symbol):
    system_message = f"""
    You are an intelligent laptop gadget expert and you are tasked with the objective to \
    solve the user queries about any product from the catalogue: {products}.\
    You should keep the user profile in mind while answering the questions.\

    Start with a brief summary of each laptop in the following format, in decreasing order of price of laptops:
    1. <Laptop Name> : <Major specifications of the laptop>, <Price in {currency_symbol}>
    2. <Laptop Name> : <Major specifications of the laptop>, <Price in {currency_symbol}>

    """
    conversation = [{"role": "system", "content": system_message }]
    return conversation