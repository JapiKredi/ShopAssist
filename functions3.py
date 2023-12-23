
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_currency_symbol",
            "description": "Get the current currency symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency_symbol": {
                        "type": "string",
                        "description": "The currency symbol, e.g. USD for US Dollar"
                    }
                },
                "required": ["currency_symbol"]
            }
        }
    }
]


def get_chat_model_completions(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
        max_tokens = 300
    )
    return response.choices[0].message["content"]
#################






#################

def get_chat_model_completions(messages, tools=tools):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
        max_tokens = 300
    )
    
    return response.choices[0].message["content"]




###############


def chat_completion_request(messages, tools=None, model='gpt-3.5-turbo-1106'):
    json_data = {"model": model, "messages": messages}
    if tools get_currency_symbol:
        json_data.update({"tools": tools})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_currency_symbol",
            "description": "Get the current currency symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency_symbol": {
                        "type": "string",
                        "description": "The currency symbol, e.g. USD for US Dollar"
                    }
                },
                "required": ["currency_symbol"]
            }
        }
    }
]


# In the following code we are forcing the model to use the get_n_day_weather_forecast function by specifying the tool_choice parameter in the chat_completion_request function.
messages = []
messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": "What currency do you want to use?"})
messages.append({"role": "system", "content": "Please try to get the currency the user wants to use, and convert this in the currecny symbol that consists of 3 capital letters"})

chat_response = chat_completion_request(
    messages, tools=tools, tool_choice={"type": "function", "function": {"name": "get_currency_symbol"}}
)

assistant_message = chat_response.json()["choices"][0]["message"]
messages.append(assistant_message)
print(assistant_message)
pretty_print_conversation(messages)








###############

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
def main():
    currency_symbol = 'USD'
    inr_value, currency_value = get_currency_value(currency_symbol)
    print(f"The value of INR is: {inr_value}")
    print(f"The value of {currency_symbol} is: {currency_value}")

# Call the main function
main()