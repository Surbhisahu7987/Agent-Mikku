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
    def __init__(self, 
                 model_name: str,
                 model_provider: ModelProvider = ModelProvider.GOOGLE,
                 model_params: dict | None = None,
                 agent_type: AgentType = AgentType.MASTER,
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

    async def call_node(self, state: dict):
        """
        Orchestrator node logic. SRP: Encapsulates how the Master Agent 
        processes state and decides on tools.
        """
        model_with_tools = self.model.bind_tools(self.tools)
        
        sys_prompt = self.system_prompt
        if hasattr(sys_prompt, "template"):
            sys_prompt = sys_prompt.template
            
        messages = [SystemMessage(content=str(sys_prompt))] + state["messages"]
        
        logger.info(f"Invoking {self.agent_type.value} model.")
        response = await model_with_tools.ainvoke(messages)
        
        return {"messages": [response]}

    # def get_tools(self) -> list[Callable]:
    #     """
    #     Retrieve tools for the Master Agent.
    #     """
    #     logger.info(f"Retrieving tools for {self.agent_type.value} agent.")
    #     # return [add_numbers]
    #     return super().get_tools()

    
async def main():
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