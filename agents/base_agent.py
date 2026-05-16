"""
This module defines the abstract base classes for AI agents in the Swiggy Builder ecosystem.
It provides foundational logic for model initialization, agent orchestration, 
tool management via the ToolRegistry, and response generation handling.
"""
import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from dotenv import load_dotenv
from typing import Any
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage
from langchain_core.callbacks import get_usage_metadata_callback
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from schema.agent_type import AgentType
from schema.model_provider import ModelProvider
from tools.tools_registry import ToolRegistry
from utils.logger import logger

load_dotenv()

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Encapsulates common attributes and methods for initializing language models
     and creating agent executors with specific tools and configurations.
    """
    def __init__(self, 
                 model_name: str, 
                 model_provider: ModelProvider,
                 system_prompt: str | PromptTemplate,
                 agent_type: AgentType,
                 model_params: dict | None = None,
                 agent_config: dict | None = None,
                 mcp_tools: list[Callable] | None = None,
                 cache_system_prompt: bool = True
                 ) -> None:
        """
        Initializes the BaseAgent with model and provider configurations.

        Args:
            model_name (str): The name/ID of the language model (e.g., 'gpt-4o').
            model_provider (ModelProvider): The provider service (e.g., GOOGLE, OPENAI).
            system_prompt (str | PromptTemplate): The system instructions defining the agent's behavior.
            agent_type (AgentType): The functional type of the agent (e.g., MASTER, SWIGGY).
            model_params (dict | None, optional): Additional parameters for the LLM. Defaults to None.
            agent_config (dict | None, optional): Configuration for the LangChain agent/graph. Defaults to None.
            mcp_tools (list[Callable] | None, optional): Tools provided via MCP. Defaults to None.
            cache_system_prompt (bool, optional): Whether to enable prompt caching if supported. Defaults to True.
        """
        self.agent_type = agent_type 
        self.model_name = model_name
        self.model_provider = model_provider
        self.model_params = model_params or {}
        self.agent_config = agent_config or {}
        self.system_prompt = system_prompt
        self.cache_system_prompt = cache_system_prompt
        self.cache = None # Placeholder for caching mechanism if needed
        self.mcp_tools = mcp_tools or []
        # Retrieve the access token from the ModelProvider Enum
        # self.access_token = model_provider.token
    
    def init_model(self, 
                   model_name: str, 
                   model_provider: ModelProvider,
                   model_params: dict
                   ) -> BaseChatModel:
        """
        Initializes the chat model using the specified provider and parameters.

        Args:
            model_name (str): The specific model version to load.
            model_provider (ModelProvider): The backend provider to use.
            model_params (dict): Configuration overrides (temperature, max_tokens, etc.).

        Returns:
            BaseChatModel: An initialized LangChain chat model instance.
        """
        logger.info(f"Initializing model for {self.agent_type.value} agent.")

        defaults = {
        "temperature": 0.7,
        "top_k": 5,
        "top_p": 0.9,
        "seed": 42,
        "max_tokens": os.environ.get("MAX_TOKENS", 1000),
        "max_retries": 3, 
        # "thinking_level": "low"
    }
        model_params = {**defaults, **model_params}

        try:
            model = init_chat_model(model=model_name,
                                    model_provider=model_provider.value,
                                    # api_key=self.access_token,
                                    **model_params
                                )
            
            logger.info(f"Model initialized successfully: {model_name} from {model_provider.value}")
            return model
              
        except Exception as e:
            logger.error(f"Error initializing model: {e}", exc_info=True)
            raise e
         
    def init_agent(self, model: BaseChatModel, agent_config: dict | None = None) -> Any:
        """
        Initializes the agent executor or workflow for the specific agent type.

        Args:
            model (BaseChatModel): The language model to power the agent.
            agent_config (dict | None, optional): Runtime configuration for the agent. Defaults to None.

        Returns:
            Any: The initialized agent executor or graph.
        """
        try:
            agent = create_agent(model=model, 
                                tools=self.tools,
                                name=self.agent_type.value,
                                system_prompt=self.system_prompt, 
                                **(agent_config or self.agent_config)
                                )
            logger.info(f"{self.agent_type.value} Agent initialized successfully with model: {self.model_name}")
            return agent
        
        except Exception as e:
            logger.error(f"Error initializing agent: {e}", exc_info=True)
            raise e
        
    def get_tools(self) -> list[Callable]:
        """
        Retrieves the tools associated with the agent's type from the ToolRegistry.

        Returns:
            list[Callable]: A list of callable tools available to the agent.
        """
        logger.info(f"Initializing tools for {self.agent_type.value} agent.")
        try:
            tools = ToolRegistry.get_tools_for_agent(self.agent_type)
            logger.info(f"Retrieved tools for {self.agent_type.value} agent")
        except Exception as e:
            logger.error(f"Error retrieving tools for {self.agent_type.value} agent: {e}", exc_info=True)
            raise e
        return tools
    
    async def generate_response(self, query: str | dict ) -> Any:
        """
        Asynchronously generates a response for a user query by streaming agent steps.

        Args:
            query (str | dict): The user input or state dictionary to process.

        Returns:
            Any: The text content of the final AI message if successful.
        """
        try:
            async for step in self.agent_executor.astream({"messages": [{"role": "user", "content": query}]},
                                                          config={"configurable": {"thread_id": "1"}}
                                                          ):
                    
                for update in step.values():
                    for message in update.get("messages", []):
                        # message.pretty_print()

                        if isinstance(message, AIMessage):
                            if message.text:
                                logger.info(f"Token Usage: {message.usage_metadata}")
                                return message.text
                        else:
                            message.pretty_print()

                        
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)

    
class BaseStructuredAgent(BaseAgent):
    """
    A base class for agents that must produce output conforming to a specific schema.
    """
    @abstractmethod
    def generate_structured_response(self, query: str | PromptTemplate):
        """
        Abstract method to generate a schema-conforming response.

        Args:
            query (str | PromptTemplate): The input prompt or template used for generation.

        Returns:
            The structured data output as defined by the implementing class.
        """
        pass 
        