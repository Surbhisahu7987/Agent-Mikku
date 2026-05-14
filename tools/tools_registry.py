from typing import Callable, List, Dict, Sequence
from langchain_core.tools import BaseTool
from schema.agent_type import AgentType
from tools.master_agent_tools import  manage_instamart_order, manage_swiggy_order, get_state
from tools.instamart_tools import search_ingredients_recipe
from tools.swiggy_tools import (calculate_restaurant_utility_score, verify_order_feasibility,
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
            # get_recipe, 
            # check_inventory
        ],
        AgentType.SWIGGY: [
            # calculate_restaurant_utility_score, 
            # verify_order_feasibility, 
            # format_swiggy_response,
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
        Returns the list of tools for a specific agent.
        Returns an empty list if the AgentType is not found.
        """
        return cls.REGISTRY.get(agent_type, [])