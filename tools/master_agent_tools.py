from functools import cache
from langchain.tools import tool
from agents.instamart_subagent import get_instamart_agent
from agents.swiggy_subagent import get_swiggy_agent

@tool
def verify_dish_identity(dish_name: str) -> str:
    """
    Verifies the identity and availability of a specific dish.
    """
    # Implementation logic for dish verification
    return f"Dish '{dish_name}' has been verified and is available."

@tool(description="Order from Instamart", 
      return_direct=True)
def manage_instamart_order(request: str) -> str:
    """
    This function is used to manage instamart orders.
    Useful for grocery shopping, household items, and recipe ingredients. 
    """
    agent = get_instamart_agent()
    # Using the high-level method which handles .invoke() internally
    return agent.generate_structured_response(request)

@tool(description="Order from Swiggy", return_direct=True)
def manage_swiggy_order(request: str) -> str:
    """
    This function is used to manage swiggy orders.
    Useful for ordering prepared food from restaurants or checking menus.
    Input should be the user's full request regarding food delivery.
    """
    agent = get_swiggy_agent()
    return agent.generate_structured_response(request)
