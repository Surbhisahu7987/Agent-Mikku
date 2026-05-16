"""
This module defines the MasterAgent class, which serves as the central orchestrator
in the Swiggy Builder ecosystem. It is responsible for analyzing user intent,
managing delivery context, and routing requests to specialized sub-agents.
"""
import os
from collections.abc import Callable
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, BaseMessage
# from langchain_google_genai import create_context_cache
from agents.base_agent import BaseAgent
from prompts.master_agent_prompt import system_prompt as master_agent_prompt
from schema.agent_type import AgentType
from schema.model_provider import ModelProvider
from utils.logger import logger

load_dotenv()

class MasterAgent(BaseAgent):
    """
    The MasterAgent acts as the primary interface and decision-maker.
    It coordinates between various tools and sub-agents to fulfill complex user
    requests related to food delivery and grocery shopping.
    """
    def __init__(self, 
                 model_name: str,
                 model_provider: ModelProvider = ModelProvider.GOOGLE,
                 model_params: dict | None = None,
                 agent_type: AgentType = AgentType.MASTER,
                 system_prompt: str | PromptTemplate = master_agent_prompt,
                 agent_config: dict | None = None
                 ):
        """
        Initializes the MasterAgent with orchestration-specific configurations.

        Args:
            model_name (str): The name/ID of the language model to use.
            model_provider (ModelProvider): The provider service. Defaults to ModelProvider.GOOGLE.
            model_params (dict | None): Optional parameters for the LLM. Defaults to None.
            agent_type (AgentType): The functional type, fixed to MASTER for this class.
            system_prompt (str | PromptTemplate): The core instructions for the orchestrator.
            agent_config (dict | None): Configuration for the LangGraph/LangChain execution.
        """
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
        
        # self.cache = create_context_cache(
        #     model=self.model,
        #     messages=[SystemMessage(content=self.system_prompt)],
        #     ttl="3600s"  # Cache expiry time in seconds
        # )
        
        self.agent_executor = self.init_agent(model=self.model, 
                                              agent_config=self.agent_config)
        

        # image_data = self.agent_executor.get_graph().draw_mermaid_png()

        # # 2. Open a file in 'wb' (write binary) mode and save
        # with open("agent_workflow.png", "wb") as f:
        #     f.write(image_data)

async def main():
    """
    Main entry point for testing the MasterAgent's response generation independently.
    """
    model_name = os.environ.get("MASTER_AGENT_MODEL", "gpt-4")
    model_provider = os.environ.get("MASTER_AGENT_MODEL_PROVIDER", "google_genai")
    master_agent = MasterAgent(model_name=model_name,
                               model_provider=ModelProvider(model_provider))
    
    query = "Recommend top restaurants serving Biryani from Swiggy."

    response = await master_agent.generate_response(query)
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())