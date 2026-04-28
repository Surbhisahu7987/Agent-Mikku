from langchain.tools import tool

@tool
def get_dish_name(user_input):
    return user_input.strip().split("for")[-1].strip()

@tool
def get_recipe_details(recipe):
    return {
        "dish_name": recipe.get("dish_name", ""),
        "ingredients": get_ingredient_list(recipe.get("ingredients", "")),
        "instructions": recipe.get("instructions", "")
    }

@tool
def get_ingredient_list(ingredient_string):
    return [ing.strip() for ing in ingredient_string.split(",")]

@tool
def format_recipe_response(recipe):    
    return f"Recipe for {recipe['dish_name']}:\nIngredients: {', '.join(recipe['ingredients'])}\nInstructions: {recipe['instructions']}"

@tool
def format_swiggy_response(restaurants):

    formatted = "Here are some restaurants that can deliver your dish:\n"

    for rest in restaurants:

        formatted += f"- {rest['name']} (Rating: {rest['rating']}, Delivery Time: {rest['delivery_time']} mins)\n"

    return formatted
