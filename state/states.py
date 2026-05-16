"""
This module defines the state schemas and data models used by the Swiggy Builder agents.
It includes Pydantic models for domain entities (Food, Delivery, Products) and 
a TypedDict for maintaining the orchestrated agent state across LangGraph nodes.
"""
from typing import TypedDict, Annotated, List, Union, Optional, Literal
import operator
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

class IdentifiedFood(BaseModel):
    """Represents culinary items identified from user input or visual analysis."""
    dish_name: str = Field(description="The name of the identified dish.")
    components: List[str] = Field(description="List of individual ingredients or parts of the dish.")
    is_food: bool = Field(description="Boolean flag indicating if the input was successfully identified as food.")
    description: str = Field(description="An appetizing and concise description of the food item for the UI.")

class DeliveryContext(BaseModel):
    """Stores location and verification details for food/grocery delivery."""
    address_id: str = Field(description="The unique identifier for the delivery address.")
    address_label: Optional[str] = Field(None, description="Human-readable label like 'Home' or 'Work'.")
    full_address: str = Field(description="The complete street address string.")
    is_verified: Optional[bool] = Field(False, description="Whether the delivery address has been confirmed by the user.")

class ProductInfo(BaseModel):
    """Detailed information for a specific product available on Instamart."""
    spin_id: str = Field(description="Unique identifier for the product (Spin ID) in the Instamart catalog.")
    name: str = Field(description="The display name of the product.")
    price: float = Field(description="The unit price of the item.")
    quantity: int = Field(description="The number of units or package size.")
    store_id: Optional[str] = Field(None, description="The identifier for the specific dark store where the product is available.")

class CustomAgentState(TypedDict):
    """
    Defines the shared state maintained across the LangGraph orchestration workflow.
    
    Attributes:
        messages: Full conversation history, using operator.add to append new messages.
        current_dish: The dish currently being processed or searched for.
        recipe_details: Raw dictionary containing ingredients and cooking steps.
        subagent_output: The text or structured output from a sub-agent's last turn.
        identified_food: Structured identification of food items from input.
        order_mode: User's intent (make at home vs order ready-to-eat).
        delivery_context: Active delivery settings for the session.
        instamart_prod: List of products staged for the Instamart cart.
        staged_options: Ranked options (restaurants or items) presented to the user.
        user_selection: The user's choice from the staged options (index or name).
        cart_summary: Final summary of items in the cart before checkout.
        pending_confirmation: If True, indicates the workflow is waiting for a Human-in-the-Loop event.
        current_step: Tracks the current phase of the agentic workflow.
    """
    # 1. Full Conversation History
    messages: Annotated[List[BaseMessage], operator.add]

    # Specific context shared between subagents
    current_dish: str
    recipe_details: dict
    subagent_output: str

    # 2. Visual/Input Identification
    identified_food: IdentifiedFood
    instamart_prod: List[ProductInfo]

    # 3. User Intent & Delivery Context
    order_mode: Literal["make", "order", "none"]
    delivery_context: DeliveryContext

    # 4. Selection Staging (HIL Support)
    staged_options: List[dict]
    user_selection: Optional[Union[int, str]]
    cart_summary: Optional[dict]

    # 5. Workflow Control
    pending_confirmation: bool  # Forces the graph to wait for user input
    current_step: str  # e.g., "identifying", "browsing", "cart_review", "tracking"