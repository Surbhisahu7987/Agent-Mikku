import os
from collections.abc import Sequence, Callable
from dotenv import load_dotenv
from functools import cache
from langchain_core.prompts import PromptTemplate
from agents.base_agent import BaseStructuredAgent
from mcp_client import SwiggyMCPManager
from schema.agent_type import AgentType
from schema.model_provider import ModelProvider
from prompts.instamart_subagent_prompt import instamart_agent_prompt
load_dotenv()

class InstaMartAgent(BaseStructuredAgent):
    def __init__(self, model_name: str = "MasterOrchestratorModel",
                 model_provider: ModelProvider = ModelProvider.GOOGLE,
                 model_params: dict | None = None,
                 system_prompt: str | PromptTemplate = instamart_agent_prompt,
                 agent_config: dict | None = None
                 ):
        
        agent_type = AgentType.INSTAMART
        
        super().__init__(model_name=model_name,
                         model_provider=model_provider,
                         agent_type=agent_type,
                         system_prompt=system_prompt,
                         model_params=model_params,
                         agent_config=agent_config)
        
        # Initialize tools based on the agent type
        self.tools = self.get_tools()

        # Initialize the model and agent executor
        self.model = self.init_model(model_name=self.model_name, 
                                     model_provider=self.model_provider, 
                                     model_params=self.model_params)
        
        self.agent_executor = self.init_agent(model=self.model, 
                                              agent_config=self.agent_config)

    
    def get_tools(self) -> list[Callable]:
        """
        This function is used to get the instamartagent's tools.
        """
        mcp_tools = SwiggyMCPManager.get_instamart_tools()
        tools = super().get_tools()  # Get base tools if any
        tools.extend(mcp_tools)  # Add MCP tools to the agent's toolset

        return tools

    def generate_structured_response(self, request: str) -> str:
        """
        This function is used to generate a structured response for the given request.
        """
        response = self.agent_executor.invoke(request)
        return response
    



# Lazy initialization prevents resource-heavy instantiation at import time.
# This is more secure and efficient for production environments.

@cache
def get_instamart_agent() -> InstaMartAgent:
    return InstaMartAgent(
        model_name="InstamartAgentModel",
        model_provider=ModelProvider.GOOGLE,
        model_params={"temperature": 0.7},
        agent_config={}
    )


