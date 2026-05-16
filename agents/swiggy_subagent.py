"""
This module defines the SwiggyAgent class, a specialized sub-agent responsible for 
handling restaurant discovery, menu matching, and food delivery logistics 
using the Swiggy Food service integrations.
"""
import os
import mlflow
from collections.abc import Callable
from async_lru import alru_cache
from dotenv import load_dotenv
from langchain_core.callbacks import get_usage_metadata_callback
from langchain_core.prompts import PromptTemplate
from agents.base_agent import BaseAgent
from mcp_client.mcp_client import SwiggyMCPManager
from schema.agent_type import AgentType
from schema.model_provider import ModelProvider
from prompts.swiggy_subagent_prompt import system_prompt as swiggy_subagent_prompt
from utils.common import _deep_make_hashable, _deep_make_dict
from utils.logger import logger

load_dotenv()

mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
mlflow.set_experiment(os.environ.get("SWIGGY_MLFLOW_EXP_NAME", "Swiggy Agent"))
mlflow.langchain.autolog()

class SwiggyAgent(BaseAgent):
    """
    A specialized agent for interacting with Swiggy Food delivery services.
    It utilizes tools for restaurant search and menu retrieval, inheriting 
    base functionalities for model initialization and execution.
    """
    def __init__(self, model_name: str = "MasterOrchestratorModel",
                 model_provider: ModelProvider = ModelProvider.GOOGLE,
                 model_params: dict | None = None,
                 system_prompt: str | PromptTemplate = swiggy_subagent_prompt,
                 agent_config: dict | None = None,
                 mcp_tools: list[Callable] | None = None
                 ):
        """
        Initializes the SwiggyAgent with specific model and tool configurations.

        Args:
            model_name (str): Name of the model to be used. Defaults to "MasterOrchestratorModel".
            model_provider (ModelProvider): The provider of the LLM. Defaults to ModelProvider.GOOGLE.
            model_params (dict | None): Configuration parameters for the model. Defaults to None.
            system_prompt (str | PromptTemplate): Instructions for the agent. Defaults to swiggy_subagent_prompt.
            agent_config (dict | None): Configuration for the agent execution. Defaults to None.
            mcp_tools (list[Callable] | None): Tools fetched via MCP. Defaults to None.
        """
        agent_type = AgentType.SWIGGY
        
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
                                              agent_config=self.agent_config,
                                              )
        
    @classmethod
    async def get_mcp_tools(cls) -> list[Callable]:
        """
        Retrieves the list of tools specific to Swiggy from the MCP manager.

        Returns:
            list[Callable]: A list of tools available for Swiggy Food operations.
        """
        mcp_tools = await SwiggyMCPManager.get_swiggy_tools()
        
        return mcp_tools

    async def generate_response(self, request: str) -> str:
        """
        Generates a response for a food delivery or restaurant-related request.

        Args:
            request (str): The user query string.

        Returns:
            str: The agent's generated text response.
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
async def get_swiggy_agent(model_params: dict | None = None,
                     agent_config: dict | None = None) -> SwiggyAgent:
    """
    A factory function to create and cache an instance of the SwiggyAgent.
    Handles dictionary-to-hashable conversion to prevent caching errors.

    Args:
        model_params (dict | None): Model specific parameters. Defaults to None.
        agent_config (dict | None): Agent specific configuration. Defaults to None.

    Returns:
        SwiggyAgent: A cached instance of the SwiggyAgent.
    """
    params_key = _deep_make_hashable(model_params) if model_params else None
    config_key = _deep_make_hashable(agent_config) if agent_config else None
    
    return await _get_swiggy_agent_cached(params_key, config_key)

@alru_cache(maxsize=1)
async def _get_swiggy_agent_cached(params_key: frozenset | None, 
                                  config_key: frozenset | None) -> SwiggyAgent:
    """Internal cached factory logic.
    
    
    """
    model_name = os.environ.get("SWIGGY_SUBAGENT_MODEL", "gpt-4")
    model_provider = os.environ.get("SWIGGY_SUBAGENT_MODEL_PROVIDER", "google") 

    mcp_tools = await SwiggyAgent.get_mcp_tools()
    
    # Convert keys back to dictionaries for the class constructor
    model_params = dict(params_key) if params_key else None
    agent_config = dict(config_key) if config_key else None
    # Reconstruct original dictionary structure
    model_params = _deep_make_dict(params_key) if params_key else None
    agent_config = _deep_make_dict(config_key) if config_key else None

    return SwiggyAgent(model_name=model_name,
                       model_provider=ModelProvider(model_provider),
                       model_params=model_params,
                       system_prompt=swiggy_subagent_prompt,
                       agent_config=agent_config,
                       mcp_tools=mcp_tools)