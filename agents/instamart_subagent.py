import os
from collections.abc import Sequence, Callable
from async_lru import alru_cache
from dotenv import load_dotenv
from functools import lru_cache
from langchain_core.callbacks import get_usage_metadata_callback
from langchain_core.prompts import PromptTemplate
from agents.base_agent import BaseAgent
from mcp_client.mcp_client import SwiggyMCPManager
from schema.agent_type import AgentType
from schema.model_provider import ModelProvider
from prompts.instamart_subagent_prompt import system_prompt as instamart_agent_prompt
from utils.logger import logger

load_dotenv()

class InstaMartAgent(BaseAgent):
    def __init__(self, model_name: str = "MasterOrchestratorModel",
                 model_provider: ModelProvider = ModelProvider.GOOGLE,
                 model_params: dict | None = None,
                 system_prompt: str | PromptTemplate = instamart_agent_prompt,
                 agent_config: dict | None = None,
                 mcp_tools: list[Callable] | None = None
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
        self.tools.extend(mcp_tools or [])  # Add MCP tools if provided
        
        # Initialize the model and agent executor
        self.model = self.init_model(model_name=self.model_name, 
                                     model_provider=self.model_provider, 
                                     model_params=self.model_params)
        
        self.agent_executor = self.init_agent(model=self.model, 
                                              
                                              agent_config=self.agent_config)

    @classmethod
    async def get_mcp_tools(self) -> list[Callable]:
        """
        This function is used to get the instamartagent's tools.
        """
        mcp_tools = await SwiggyMCPManager.get_instamart_tools()

        return mcp_tools

    async def generate_response(self, request: str) -> str:
        """
        This function is used to generate a structured response for the given request.
        """
        inputs = {"messages": [{"role": "user", "content": request}]}

        try:
            print(f"Generating response for query: {request}")
            with get_usage_metadata_callback() as callback:
                
                response = await self.agent_executor.ainvoke(inputs)
                logger.info(callback.usage_metadata)
                return response["messages"][-1].text
        
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
        

@alru_cache(maxsize=1)
async def get_instamart_agent(model_params: dict | None = None, 
                        agent_config: dict | None = None) -> InstaMartAgent:
    """
    Factory function to get a cached instance of the InstaMartAgent.
    """
    model_name = os.environ.get("INSTAMART_SUBAGENT_MODEL", "gpt-4")
    model_provider = os.environ.get("INSTAMART_SUBAGENT_MODEL_PROVIDER", "google")

    mcp_tools = await InstaMartAgent.get_mcp_tools()

    return InstaMartAgent(model_name=model_name,
                          model_provider=ModelProvider(model_provider),
                          model_params=model_params,
                          system_prompt=instamart_agent_prompt,
                          agent_config=agent_config,
                          mcp_tools=mcp_tools)

