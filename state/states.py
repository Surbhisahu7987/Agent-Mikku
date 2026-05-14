from typing import TypedDict, Annotated, List, Union, Optional, Literal
import operator
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

class IdentifiedFood(BaseModel):
    dish_name: str 
    components: List[str]
    is_food: bool
    description: str  # Appetizing description for the UI

class DeliveryContext(BaseModel):
    address_id: str
    address_label: Optional[str]  # e.g., "Home", "Work"
    full_address: str
    is_verified: Optional[bool]

class ProductInfo(BaseModel):
    spin_id: str 
    name: str
    price: float
    quantity: int
    store_id: Optional[str]

class CustomAgentState(TypedDict):
    # 1. Full Conversation History
    messages: Annotated[List[BaseMessage], operator.add]

    # Specific context shared between subagents
    current_dish: str
    recipe_details: dict
    subagent_output: str

    # 2. Visual/Input Identification
    identified_food: IdentifiedFood

    # 3. User Intent & Delivery Context
    order_mode: Literal["make", "order", "none"]
    delivery_context: DeliveryContext

    # 4. Selection Staging (HIL Support)
    instamart_prod: List[ProductInfo]
    staged_options: List[dict]
    user_selection: Optional[Union[int, str]]
    cart_summary: Optional[dict]

    # 5. Workflow Control
    pending_confirmation: bool  # Forces the graph to wait for user input
    current_step: str  # e.g., "identifying", "browsing", "cart_review", "tracking"