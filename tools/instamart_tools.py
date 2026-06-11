from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun


@tool
def format_recipe_response(recipe):  
    """
    This tool provides a simple interface to format the recipe response.
    Args: 
        recipe (dict): A dictionary containing the recipe information.
    Returns:
        str: A string containing the formatted recipe information.
    """  
    return f"Recipe for {recipe['dish_name']}:\nIngredients: {', '.join(recipe['ingredients'])}\nInstructions: {recipe['instructions']}"


@tool
def search_ingredients_recipe(query: str) -> str:
    '''
    This tool provides a simple interface to search for recipes based on dish name.
    Args:
        query (str): Name of dish for which ingredients or recipes you need to search for.
    Returns:
        str: List of Ingredients and recipes
    
    '''
    search = DuckDuckGoSearchRun()
    return search.run(query)



