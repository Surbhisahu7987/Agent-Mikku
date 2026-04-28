import os
from dotenv import load_dotenv
from agents.base_agent import BaseAgent
from tools.master_agent_tools import *
load_dotenv()

class MasterAgent(BaseAgent):
    def __init__(self, model_name: str, tools: list = []):
        
        super().__init__(model_name, tools=tools)

    