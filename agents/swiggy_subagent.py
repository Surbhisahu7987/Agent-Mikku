import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from tools.swiggy_tools import *

load_dotenv()

class SwiggyAgent:
    def __init__(self, model_name: str, tools: list = []):
        
        super().__init__(model_name, tools=tools)

    