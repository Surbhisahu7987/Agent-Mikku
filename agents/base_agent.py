from abc import ABC, abstractmethod
from collections.abc import Sequence, Callable
from typing import Any
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from schema.agent_type import AgentType
from swiggy_builder_agents.schema.model_provider import ModelProvider
from utils.logger import logger

class BaseAgent(ABC):
    def __init__(self, 
                 model_name: str, 
                 model_provider: ModelProvider,
                 system_prompt: str | PromptTemplate,
                 agent_type: AgentType | None = None,
                 model_params: dict | None = None,
                 ) -> None:
        
        self.agent_type = agent_type 
        self.model_name = model_name
        self.model_provider = model_provider
        self.model_params = model_params or {}
        self.system_prompt = system_prompt

        # Retrieve the access token from the ModelProvider Enum
        self.access_token = model_provider.token

        # Initialize tools based on the agent type
        self.tools = self.get_tools(self.agent_type)

        # Initialize the model and agent executor
        self.model = self.init_model(self.model_name, self.model_provider, self.model_params)
        self.agent_executor = self.init_agent(self.model)

    
    def init_model(self, 
                   model_name: str, 
                   model_provider: ModelProvider,
                   model_params: dict
                   ) -> BaseChatModel:
        """
        This function is used to initialize the model.
        """
        defaults = {
        "temperature": 0.7,
        "max_new_tokens": 512,
        "top_k": 5,
        "top_p": 0.9,
        "seed": 42
    }
        model_params = {**defaults, **model_params}

        try:
            model = init_chat_model(model=model_name,
                                    model_provider=model_provider.value,
                                    api_key=self.access_token,
                                    **model_params
                                )
            return model
              
        except Exception as e:
            logger.error(f"Error initializing model: {e}", exc_info=True)
            raise e
         

    def init_agent(self, model: BaseChatModel, **kwargs):
        """
        This function is used to initialize the agent.
        """
        try:
            agent = create_agent(model=model, 
                                tools=self.tools,
                                system_prompt=self.system_prompt, 
                                **kwargs
                                )
            return agent
        
        except Exception as e:
            logger.error(f"Error initializing agent: {e}", exc_info=True)
            raise e
    
    @abstractmethod
    def get_tools(self, agent_type: str) -> Sequence[Callable]:
        """
        This function is used to get the agent's tools.
        """
        pass
    
    @abstractmethod
    def generate_response(self, query: str | PromptTemplate) -> Any:
        """
        This function is used to generate a response for a given query.
        """
        pass

class BaseStructuredAgent(BaseAgent):

    @abstractmethod
    def generate_structured_response(self, query: str | PromptTemplate):
        """
        This function is used to generate a structured response for a given query.
        """
        pass 
        