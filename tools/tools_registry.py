"""
This module serves as a centralized management system for agent tools.
It maps various AgentTypes to their respective collections of LangChain-compatible tools,
ensuring that each agent has access only to its permitted capabilities.
"""
from typing import Callable, List, Dict, Sequence
from langchain_core.tools import BaseTool
from schema.agent_type import AgentType
from tools.master_agent_tools import  manage_instamart_order, manage_swiggy_order, get_state
from tools.instamart_tools import search_ingredients_recipe
from tools.swiggy_tools import (verify_order_feasibility,
                                format_swiggy_response, )

class ToolRegistry:
    """
    A centralized registry mapping AgentTypes to their respective 
    lists of LangChain tool callables.
    """
    
    # The Mapping: One lookup to get all tools for an agent
    REGISTRY = {
        AgentType.INSTAMART: [
            search_ingredients_recipe, 
        ],
        AgentType.SWIGGY: [
            verify_order_feasibility, 
            format_swiggy_response,
        ],
        AgentType.MASTER: [
            manage_instamart_order,
            manage_swiggy_order,
            get_state
        ]
    }

    @classmethod
    def get_tools_for_agent(cls, agent_type: AgentType) -> List[BaseTool]:
        """
        Retrieves the collection of tools associated with a specific agent type.

        Args:
            agent_type (AgentType): The identifier for the agent (e.g., MASTER, SWIGGY) 
                whose tools need to be fetched.

        Returns:
            List[BaseTool]: A list of tools available for the specified agent. 
                Returns an empty list if the agent type is not found in the registry.
        """
        return cls.REGISTRY.get(agent_type, [])