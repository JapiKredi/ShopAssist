# Submission 

from flask import Flask, redirect, url_for, render_template, request
from functions8 import initialize_conversation, initialize_conv_reco, get_chat_model_completions, moderation_check,intent_confirmation_layer,dictionary_present,compare_laptops_with_user,recommendation_validation, get_budget, get_currency_value

import openai
import ast
import re
import pandas as pd
import json
import os
import requests

# Read the OpenAI Api_key
openai.api_key = open("OpenAI_API_Key.txt", "r").read().strip()

# Read the Currency converter Api_key
API_KEY = open("API_Key.txt", "r").read().strip()

# The code app = Flask(__name__) creates an instance of the Flask class in Python.
# The Flask class is a part of the Flask framework, which is a popular web framework used for building web applications in Python. It provides a set of tools and libraries for handling HTTP requests, routing, and rendering HTML templates.
app = Flask(__name__)

# This line initializes an empty list called conversation_bot.
# This list will be used to store conversation data.
conversation_bot = []
conversation = initialize_conversation()
introduction = get_chat_model_completions(conversation)

# The code conversation_bot.append({'bot': introduction}) appends a new dictionary to the conversation_bot list. 
# The dictionary contains a key-value pair where the key is 'bot' and the value is the variable introduction.
conversation_bot.append({'bot':introduction})

# The code top_3_laptops = None assigns the value None to the variable top_3_laptops.
top_3_laptops = None


@app.route("/")
def default_func():
    global conversation_bot, conversation, top_3_laptops, API_KEY
    return render_template("index_invite.html", name_xyz = conversation_bot)

@app.route("/end_conv", methods = ['POST','GET'])
def end_conv():
    global conversation_bot, conversation, top_3_laptops, API_KEY
    conversation_bot = []
    conversation = initialize_conversation()
    introduction = get_chat_model_completions(conversation)
    conversation_bot.append({'bot':introduction})
    top_3_laptops = None
    return redirect(url_for('default_func'))

@app.route("/invite", methods = ['POST'])
def invite():
    global conversation_bot, conversation, top_3_laptops, conversation_reco, API_KEY
    user_input = request.form["user_input_message"]
    prompt = 'Remember your system message and that you are an intelligent laptop assistant. So, you only help with questions around laptop.'
    moderation = moderation_check(user_input)
    if moderation == 'Flagged':
        return redirect(url_for('end_conv'))

    if top_3_laptops is None:
        conversation.append({"role": "user", "content": user_input + prompt})
        conversation_bot.append({'user':user_input})

        response_assistant = get_chat_model_completions(conversation)

        moderation = moderation_check(response_assistant)
        if moderation == 'Flagged':
            return redirect(url_for('end_conv'))

        confirmation = intent_confirmation_layer(response_assistant)

        moderation = moderation_check(confirmation)
        if moderation == 'Flagged':
            return redirect(url_for('end_conv'))

        if "No" in confirmation:
            conversation.append({"role": "assistant", "content": response_assistant})
            conversation_bot.append({'bot':response_assistant})
        else:
            response = dictionary_present(response_assistant)

            moderation = moderation_check(response)
            if moderation == 'Flagged':
                return redirect(url_for('end_conv'))
            
            print('Printing the conversation bot')
            print(conversation)
            print('running the get budget_function')
            budget_value, currency_symbol = get_budget(conversation)
            
            print('Printing the output of the function call get budget')
            print(budget_value)
            print(currency_symbol)
            
            #currency_symbol = 'USD'
            inr_value, currency_value = get_currency_value(currency_symbol)
            print(f"The value of INR is: {inr_value}")
            print(f"The value of {currency_symbol} is: {currency_value}")
            currency_conversion_rate = float(currency_value) / float(inr_value)
            print(currency_conversion_rate)
                        
            conversation_bot.append({'bot':"Thank you for providing all the information. Kindly wait, while I fetch the products: \n"})
            top_3_laptops = compare_laptops_with_user(response, currency_conversion_rate, currency_symbol)

            validated_reco = recommendation_validation(top_3_laptops)

            if len(validated_reco) == 0:
                conversation_bot.append({'bot':"Sorry, we do not have laptops that match your requirements. Connecting you to a human expert. Please end this conversation."})

            conversation_reco = initialize_conv_reco(validated_reco, currency_symbol)
            recommendation = get_chat_model_completions(conversation_reco)

            moderation = moderation_check(recommendation)
            if moderation == 'Flagged':
                return redirect(url_for('end_conv'))

            conversation_reco.append({"role": "user", "content": "This is my user profile" + response})

            conversation_reco.append({"role": "assistant", "content": recommendation})
            conversation_bot.append({'bot':recommendation})

            print(recommendation + '\n')

    else:
        conversation_reco.append({"role": "user", "content": user_input})
        conversation_bot.append({'user':user_input})

        response_asst_reco = get_chat_model_completions(conversation_reco)

        moderation = moderation_check(response_asst_reco)
        if moderation == 'Flagged':
            return redirect(url_for('end_conv'))

        conversation.append({"role": "assistant", "content": response_asst_reco})
        conversation_bot.append({'bot':response_asst_reco})
    return redirect(url_for('default_func'))

if __name__ == '__main__':
    app.run(debug=True, host= "0.0.0.0")