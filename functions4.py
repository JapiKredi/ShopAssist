import openai
import ast
import re
import pandas as pd
import json


def initialize_conversation():
    '''
    Returns a list [{"role": "system", "content": system_message}]
    '''
    
    delimiter = "####"
    example_user_req = {'GPU intensity': 'high','Display quality': 'high','Portability': 'low','Multitasking': 'high','Processing speed': 'high'}
    
    system_message = f"""

    You are an intelligent laptop gadget expert and your goal is to find the best laptop for a user.
    You need to ask relevant questions and understand the user profile by analysing the user's responses.
    You final objective is to fill the values for the different keys ('GPU intensity','Display quality','Portability','Multitasking','Processing speed') in the python dictionary and be confident of the values.
    These key value pairs define the user's profile.
    The python dictionary looks like this {{'GPU intensity': 'values','Display quality': 'values','Portability': 'values','Multitasking': 'values','Processing speed': 'values'}}
    The values for all keys, should be 'low', 'medium', or 'high' based on the importance of the corresponding keys, as stated by user. 
    The values currently in the dictionary are only representative values. 
    
    {delimiter}Here are some instructions around the values for the different keys. If you do not follow this, you'll be heavily penalised.
    - The values for all keys should strictly be either 'low', 'medium', or 'high' based on the importance of the corresponding keys, as stated by user.
    - Do not randomly assign values to any of the keys. The values need to be inferred from the user's response.
    {delimiter}

    To fill the dictionary, you need to have the following chain of thoughts:
    {delimiter} Thought 1: Ask a question to understand the user's profile and requirements. \n
    If their primary use for the laptop is unclear. Ask another question to comprehend their needs.
    You are trying to fill the values of all the keys ('GPU intensity','Display quality','Portability','Multitasking','Processing speed') in the python dictionary by understanding the user requirements.
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
    You are provided an input. You need to evaluate if the input has the following keys: 'GPU intensity','Display quality','Portability','Multitasking',' Processing speed'
    Next you need to evaluate if the keys have the the values filled correctly.
    The values for all keys should be 'low', 'medium', or 'high' based on the importance as stated by user. 
    Output a string 'Yes' if the input contains the dictionary with the values correctly filled for all keys.
    Otherwise output the string 'No'.

    Here is the input: {response_assistant}
    Only output a one-word string - Yes or No.
    """


    confirmation = openai.Completion.create(
                                    model="text-davinci-003",
                                    prompt = prompt,
                                    temperature=0)


    return confirmation["choices"][0]["text"]


def budget_prompting():  
    delimiter = "####"
    example_user_req = {'Budget': '80000 INR'}

    
    system_message = f"""
    You final objective is to also get the budget of the user.
    The python dictionary looks like this {{'Budget': 'values'}}
    The value for 'budget' should be a numerical value and the currency as extracted from the user's response. 
    For example '1000 USD', or '1000 euro' or '80,000 indian rupees'.
    The budget value and the currency currently in the dictionary are only representative values. 
    You will have to ask the user for the answers of both the budget and also the currency. 
    
    {delimiter}Here are some instructions around the values for the different keys. If you do not follow this, you'll be heavily penalised.
    - You will have to ask the user a question in order to get the budgetof the uder for the laptop. 
    - The value for 'budget' should be a numerical value extracted from the user's response.
    - Do not randomly assign values to any of the keys. The values need to be inferred from the user's response.
    {delimiter}

    {delimiter} Here is a sample conversation between the user and assistant:
    Assistant:"Thanks for all the information. Could you kindly let me know your budget for the laptop? You can use any currency that you prefer. This will help me find options that fit within your price range while meeting the specified requirements."
    User: "My max budget is 80,000"
    Assistant:"Thanks. Which currency is this?" Please provide the currency code.
    User: "80,000 INR"
    
    Assistant: "{example_user_req}"
    {delimiter}

    Ask the user what the budget is for the laptop. Do not start with Assistant: "
    """
    conversation = [{"role": "system", "content": system_message}]
    return conversation


def get_budget__completions(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
        max_tokens = 300
    )
    return response.choices[0].message["content"]



def get_budget(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": "What is your budget for the laptop?"}],
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
    # Step 2, check if the model wants to call a function
    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        function_args = json.loads(message["function_call"]["arguments"])

        # Step 3, call the function
        # Note: the JSON response from the model may not be valid JSON
        function_response = get_budget_(
            budget_value=function_args.get("budget_value"),
            currency_symbol=function_args.get("currency_symbol"),
        )
        print(budget_value)
        print(currency_symbol)
        return budget_value, currency_symbol
        """


def budget_confirmation_layer(budget_response_assistant):
    delimiter = "####"
    prompt = f"""
    You are a senior evaluator who has an eye for detail.
    You are provided an input. You need to evaluate if the input contains a budget. 
    The correct input will contain a nummerical value and the currency. 
    Correct answers are '80,000 indian rupees', or 100,000 INR', '1000 USD', or '1000 euro' or '1,000 euro'
    Output a string 'Yes' if the input contains the budget.
    Correct answers are '80,000 indian rupees', or 100,000 INR', '1000 USD', or '1000 euro' or '1,000 euro'
    Is there is no nummercial value, then output a string 'No'.
    
    Here is the input: {budget_response_assistant}
    Only output a one-word string - 'Yes' or 'No'.
    """

    budget_confirmation = openai.Completion.create(
                                    model="text-davinci-003",
                                    prompt = prompt,
                                    temperature=0)


    return budget_confirmation["choices"][0]["text"]


def dictionary_present(response):
    delimiter = "####"
    user_req = {'GPU intensity': 'high','Display quality': 'high','Portability': 'medium','Multitasking': 'high','Processing speed': 'high'}
    prompt = f"""You are a python expert. You are provided an input.
            You have to check if there is a python dictionary present in the string.
            It will have the following format {user_req}.
            Your task is to just extract and return only the python dictionary from the input.
            The output should match the format as {user_req}.
            The output should contain the exact keys and values as present in the input.

            Here are some sample input output pairs for better understanding:
            {delimiter}
            input: - GPU intensity: low - Display quality: high - Portability: low - Multitasking: high - Processing speed: medium
            output: {{'GPU intensity': 'low', 'Display quality': 'high', 'Portability': 'low', 'Multitasking': 'high', 'Processing speed': 'medium'}}

            input: {{'GPU intensity':     'low', 'Display quality':     'high', 'Portability':    'low', 'Multitasking': 'high', 'Processing speed': 'medium'}}
            output: {{'GPU intensity': 'low', 'Display quality': 'high', 'Portability': 'low', 'Multitasking': 'high', 'Processing speed': 'medium'}}

            input: Here is your user profile 'GPU intensity': 'high','Display quality': 'high','Portability': 'medium','Multitasking': 'low','Processing speed': 'high'
            output: {{'GPU intensity': 'high','Display quality': 'high','Portability': 'medium','Multitasking': 'high','Processing speed': 'low'}}
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


def compare_laptops_with_user(user_req_string, budget, currency_conversion_factor):
    laptop_df= pd.read_csv('updated_laptop.csv')
    laptop_df['price'] = laptop_df['price'] * currency_conversion_factor
    user_requirements = extract_dictionary_from_string(user_req_string)
    user_budget = int(budget).replace(',', '').split()
    
    #This line retrieves the value associated with the key 'budget' from the user_requirements dictionary.
    #If the key is not found, the default value '0' is used.
    #The value is then processed to remove commas, split it into a list of strings, and take the first element of the list.
    #Finally, the resulting value is converted to an integer and assigned to the variable budget.

    filtered_laptops = laptop_df.copy()
    filtered_laptops['Price'] = filtered_laptops['Price'].str.replace(',','').astype(int)
    filtered_laptops = filtered_laptops[filtered_laptops['Price'] <= user_budget].copy()
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

    return top_laptops.to_json(orient='records')


def get_currency_value(currency_symbol):
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



def recommendation_validation(laptop_recommendation):
    data = json.loads(laptop_recommendation)
    data1 = []
    for i in range(len(data)):
        if data[i]['Score'] > 2:
            data1.append(data[i])

    return data1



def initialize_conv_reco(products):
    system_message = f"""
    You are an intelligent laptop gadget expert and you are tasked with the objective to \
    solve the user queries about any product from the catalogue: {products}.\
    You should keep the user profile in mind while answering the questions.\

    Start with a brief summary of each laptop in the following format, in decreasing order of price of laptops:
    1. <Laptop Name> : <Major specifications of the laptop>, <Price in Rs>
    2. <Laptop Name> : <Major specifications of the laptop>, <Price in Rs>

    """
    conversation = [{"role": "system", "content": system_message }]
    return conversation