"""
This module provides specialized tools for the Swiggy Food sub-agent.
It includes utilities for ranking restaurants based on service quality metrics,
validating order constraints, and formatting final responses for the user.
"""
from langchain.tools import tool

def calculate_restaurant_utility_score(restaurants: list[dict]) -> list[dict]:
    """
    Calculates a multi-criteria utility score for a list of restaurants.
    
    The score is weighted as follows:
    - Rating: 50%
    - Delivery Time: 30% (Inverse: faster is better)
    - Average Price: 20% (Inverse: cheaper is better)

    Args:
        restaurants (list[dict]): A list of restaurant dictionaries containing 
            'rating', 'delivery_time', and 'avg_price'.

    Returns:
        list[dict]: The top 5 restaurants sorted by their calculated utility_score in descending order.
    """
    scored_list = []
    for res in restaurants:
        # Normalize values (Assuming rating is 0-5, time is mins, price is INR)
        rating_score = float(res.get('rating', 0)) / 5.0
        
        # Inverse logic: Lower time and lower price are better
        time_val = float(res.get('delivery_time', 60))
        time_score = 1 - (min(time_val, 60) / 60) 
        
        price_val = float(res.get('avg_price', 500))
        price_score = 1 - (min(price_val, 1000) / 1000)

        utility_score = (rating_score * 0.5) + (time_score * 0.3) + (price_score * 0.2)
        res['utility_score'] = round(utility_score, 2)
        scored_list.append(res)
    
    # Sort by score descending
    return sorted(scored_list, key=lambda x: x['utility_score'], reverse=True)[:5]

@tool
def verify_order_feasibility(cart_total: float, availability_status: str) -> dict:
    """
    Validates if an order meets the specific business constraints of the Swiggy ecosystem:
    - Max Order: ₹1000
    - Restaurant must be OPEN

    Args:
        cart_total (float): The total monetary value of the items in the cart.
        availability_status (str): The current operational status of the restaurant (e.g., 'OPEN').

    Returns:
        dict: A dictionary containing:
            - feasible (bool): True if the order can proceed, False otherwise.
            - reason (str, optional): A description of the failure if not feasible.
    """
    if availability_status.upper() != "OPEN":
        return {"feasible": False, "reason": "Restaurant is currently closed."}
    
    if cart_total > 1000:
        return {"feasible": False, "reason": "Order exceeds the ₹1000 limit."}
    
    return {"feasible": True}


@tool
def format_swiggy_response(restaurants: list[dict]):
    """
    Converts a list of restaurant data into a user-friendly text summary.

    Args:
        restaurants (list[dict]): A list of restaurant objects to be displayed.

    Returns:
        str: A formatted string listing the restaurant names, ratings, and delivery times.
    """

    formatted = "Here are some restaurants that can deliver your dish:\n"

    for restaurant in restaurants:

        formatted += f"- {restaurant['name']} (Rating: {restaurant['rating']}, Delivery Time: {restaurant['delivery_time']} mins)\n"

    return formatted