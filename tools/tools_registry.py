from typing import Callable, List, Dict, Sequence
from langchain_core.tools import BaseTool
from schema.agent_type import AgentType
from tools.master_agent_tools import verify_dish_identity, manage_instamart_order, manage_swiggy_order
from tools.instamart_tools import search_items, get_recipe, check_inventory
from tools.swiggy_tools import find_restaurants, get_menu, place_order

class ToolRegistry:
    """
    A centralized registry mapping AgentTypes to their respective 
    lists of LangChain tool callables.
    """
    
    # The Mapping: One lookup to get all tools for an agent
    REGISTRY = {
        AgentType.INSTAMART: [
            search_items, 
            get_recipe, 
            check_inventory
        ],
        AgentType.SWIGGY: [
            find_restaurants, 
            get_menu, 
            place_order
        ],
        AgentType.MASTER: [
            verify_dish_identity
        ]
    }

    @classmethod
    def get_tools_for_agent(cls, agent_type: AgentType) -> List[BaseTool]:
        """
        Returns the list of tools for a specific agent.
        Returns an empty list if the AgentType is not found.
        """
        return cls.REGISTRY.get(agent_type, [])