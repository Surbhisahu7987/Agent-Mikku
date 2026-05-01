from collections.abc import Callable
from langchain_core.prompts import PromptTemplate
from agents.base_agent import BaseAgent
from prompts.master_agent_prompt import master_agent_prompt
from schema.agent_type import AgentType
from schema.model_provider import ModelProvider


class MasterAgent(BaseAgent):
    def __init__(self, model_name: str = "MasterOrchestratorModel",
                 model_provider: ModelProvider = ModelProvider.GOOGLE,
                 model_params: dict | None = None,
                 agent_type: AgentType = AgentType.MASTER_AGENT,
                 system_prompt: str | PromptTemplate = master_agent_prompt,
                 agent_config: dict | None = None
                 ):
        
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
        
        self.agent_executor = self.init_agent(model=self.model, agent_config=self.agent_config)

    def get_tools(self) -> list[Callable]:
        """
        Retrieve tools for the Master Agent.
        """
        return super().get_tools()

    def generate_response(self, query: str | PromptTemplate) -> str:
        """
        Generate a response using the agent executor.
        """
        return self.agent_executor.invoke(query)
