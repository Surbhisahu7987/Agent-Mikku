from langchain.tools import tool
from langgraph.prebuilt.tool_node import ToolRuntime
from utils.logger import logger

@tool
def resolve_delivery_context(saved_addresses: list[dict], user_hint: str = None) -> dict:
    """
    Analyzes saved addresses and matches them against any user hints (e.g., 'at work').
    If no hint is provided, it selects the 'Primary' or last used address.
    If no address is suitable, it returns a status to prompt for a new location.
    """
    if not saved_addresses:
        return {"status": "REQUEST_NEW_LOCATION", "message": "No saved addresses found."}
    
    if user_hint:
        # Simple keyword matching for 'Home', 'Work', etc.
        for addr in saved_addresses:
            if user_hint.lower() in addr.get('address_type', '').lower():
                return {"status": "SUCCESS", "address": addr}
    
    # Default to first address
    return {"status": "SUCCESS", "address": saved_addresses[0]}

@tool
def format_restaurant_menu_card(restaurant_list: list[dict]) -> str:
    """
    Transforms the top 5 restaurants into a clean, readable string 
    formatted for the Master Agent to show the user.
    """
    output = "Top 5 Recommendations for you:\n"
    for i, res in enumerate(restaurant_list, 1):
        output += (
            f"{i}. {res['name']} ({res['rating']}⭐)\n"
            f"    Time: {res['delivery_time']} mins | 💰 Price for one: ₹{res['avg_price']}\n"
            f"    Delivery Fee: ₹{res.get('delivery_fee', 0)}\n"
        )
    return output

@tool(description="Order from Instamart")
async def manage_instamart_order(request: str) -> str:
    """
    This function is used to manage instamart orders.
    Useful for grocery shopping, household items, and recipe ingredients. 
    """
    # Lazy initialization prevents resource-heavy instantiation at import time.
    from agents.instamart_subagent import get_instamart_agent
    logger.info("Invoking Instamart agent to handle the request.")
    try:
        agent = await get_instamart_agent()
        # Using the high-level method which handles .invoke() internally
        return await agent.generate_response(request)
    
    except Exception as e:
        logger.error(f"Error occurred while initializing Instamart agent: {e}")
        raise e


@tool(description="Order from Swiggy")
async def manage_swiggy_order(request: str) -> str:
    """
    This function is used to manage swiggy orders.
    Useful for ordering prepared food from restaurants or checking menus.
    Input should be the user's full request regarding food delivery.
    """

    from agents.swiggy_subagent import get_swiggy_agent
    try:
        agent = await get_swiggy_agent()
        response = await agent.generate_response(request)
        return response
    except Exception as e:
        logger.error(f"Error occurred while initializing Swiggy agent: {e}")
        raise e

@tool
async def get_state(runtime: ToolRuntime) -> str:
    """ 
    This tool retrieves the current state of the ToolRuntime.
    Useful for debugging or inspecting the execution context within the agent's workflow.
    Returns:
        str: The current state representation from the ToolRuntime.

    """
    return runtime.state