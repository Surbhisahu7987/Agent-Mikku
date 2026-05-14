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
        This function is used to initialize the model.
        """
        logger.info(f"Initializing model for {self.agent_type.value} agent.")

        defaults = {
        "temperature": 0.7,
        "top_k": 5,
        "top_p": 0.9,
        "seed": 42,
        "max_tokens": os.environ.get("MAX_TOKENS", 1000),
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
        This function is used to initialize the agent.
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
        This function is used to get the agent's tools.
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
        This function is used to generate a response for a given query.
        """
        """
        Generate a response using the agent executor.
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

    @abstractmethod
    def generate_structured_response(self, query: str | PromptTemplate):
        """
        This function is used to generate a structured response for a given query.
        """
        pass 
        