from flask import Flask, redirect, url_for, render_template, request
from functions5 import initialize_conversation, initialize_conv_reco, get_chat_model_completions, moderation_check,intent_confirmation_layer,dictionary_present,compare_laptops_with_user,recommendation_validation


import openai
import ast
import re
import pandas as pd
import json
import os


# Read the OpenAI Api_key
openai.api_key = open("OpenAI_API_Key.txt", "r").read().strip()


response = check_budget(response)

print(response)



