from typing import TypedDict, Annotated, List, Union
import operator

class AgentState(TypedDict):
    # Tracks the full conversation history
    messages: Annotated[List[dict], operator.add]
    # Specific context shared between subagents
    current_dish: str
    order_mode: str  # "make" or "order"
    recipe_details: dict
    subagent_output: str