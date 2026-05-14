from langchain.tools import tool

@tool
def calculate_restaurant_utility_score(restaurants: list[dict]) -> list[dict]:
    """
    Calculates a utility score for each restaurant based on:
    Score = (Rating * 0.5) + (Time_Inverse * 0.3) + (Price_Inverse * 0.2).
    Returns the restaurants sorted by highest score.
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
    Checks if the order complies with Swiggy Builders Club v1 constraints:
    - Max Order: ₹1000
    - Restaurant must be OPEN
    """
    if availability_status.upper() != "OPEN":
        return {"feasible": False, "reason": "Restaurant is currently closed."}
    
    if cart_total > 1000:
        return {"feasible": False, "reason": "Order exceeds the ₹1000 limit."}
    
    return {"feasible": True}


@tool
def format_swiggy_response(restaurants: list[dict]):
    """
    Transforms the top 5 restaurants into a clean, readable string 
    formatted for the Swiggy Agent to show the user.
    """

    formatted = "Here are some restaurants that can deliver your dish:\n"

    for rest in restaurants:

        formatted += f"- {rest['name']} (Rating: {rest['rating']}, Delivery Time: {rest['delivery_time']} mins)\n"

    return formatted