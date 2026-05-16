"""
This module manages the Model Context Protocol (MCP) clients for Swiggy services.
It handles tool discovery, caching, and result filtering for both Instamart 
and Swiggy Food domains.
"""
import os
import json
from dotenv import load_dotenv
from requests import HTTPError
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain_core.messages.content import TextContentBlock
from utils.logger import logger
load_dotenv()

class SwiggyMCPManager:
    """
    A centralized manager for handling MCP server connections and tool lifecycles.
    It provides methods to fetch cached tools and implements interceptors for 
    post-processing tool outputs.
    """
    
    # Caches for initialized tools
    _instamart_tools = None
    _swiggy_tools = None
    _transport = os.getenv("MCP_TRANSPORT", "streamable_http")
    TOKEN = os.getenv("MCP_ACCESS_TOKEN")
    HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

    @staticmethod
    async def im_filter_search_product(request: MCPToolCallRequest,
                                 handler):
        """Interceptor to filter and keep only the top 5 products from search results.

        This method filters the product list received from instamart's
        "search_products" tool and keeps only the top 5 products.
        This help in reduce the token bloat due to multiple irrelevant 
        products received in the tool response by a factor of 5X to 10X.

        Args:
            request (MCPToolCallRequest): The tool call request object.
            handler (Callable): The downstream handler used to execute the tool.

        Returns:
            The processed tool result containing filtered product data to reduce 
            token consumption.
        """
        
        result = await handler(request)
        logger.info(f"Calling tool: {request.name}")

        if request.name == "search_products":
            for i, msg in enumerate(result.content):
                if hasattr(msg, "text"):    
                    data = json.loads(msg.text)
                    products = []
                    for product in data.get("data", {}).get("products", [])[:5]:
                        for var in product["variations"]:
                            del var["imageUrl"]
                            products.append(var)
                    data["data"]["products"]= products
                    msg.text = json.dumps(data)
                    result.content[i] = msg
            return result
        
        return result

    @staticmethod
    async def swiggy_interceptor(request: MCPToolCallRequest,
                                 handler):
        """Interceptor for logging Swiggy Food tool calls and results.

        Args:
            request (MCPToolCallRequest): The tool call request object.
            handler (Callable): The downstream handler used to execute the tool.

        Returns:
            The tool execution result.
        """
        logger.info(f"Calling tool: {request.name}, Request: {request.args}")
        result = await handler(request)
        return result

    @classmethod
    async def get_instamart_tools(cls):
        """Fetches and caches the list of tools available for Instamart.

        Returns:
            list[Callable]: A list of callable tools provided by the Instamart 
                MCP server. Returns an empty list if an HTTP error occurs.
        """
        if cls._instamart_tools is None:
            client = MultiServerMCPClient(
                {
                "instamart": {
                    "transport": cls._transport,
                    "url": os.environ.get("INSTAMART_MCP_URL", "https://mcp.swiggy.com/im"),
                    "headers": cls.HEADERS
                    }
                },
                tool_interceptors=[SwiggyMCPManager.im_filter_search_product]
            )

            try:
                cls._instamart_tools = await client.get_tools()
                return cls._instamart_tools
            except HTTPError as e:
                logger.error(f"HTTP error occurred while fetching Instamart tools: {e}")
                return []
            except Exception as e:
                logger.error(f"Error fetching Instamart tools: {e}", exc_info=True)
                raise e
    @classmethod
    async def get_swiggy_tools(cls):
        """Fetches and caches the list of tools available for Swiggy Food.

        Returns:
            list[Callable]: A list of callable tools provided by the Swiggy 
                Food MCP server. Returns an empty list if an HTTP error occurs.
        """
        if cls._swiggy_tools is None:
            client = MultiServerMCPClient({
                "food": {
                    "transport": cls._transport,
                    "url": os.environ.get("SWIGGY_MCP_URL", "https://mcp.swiggy.com/food"),
                    "headers": cls.HEADERS
                }
            },
            tool_interceptors=[SwiggyMCPManager.swiggy_interceptor]
            )
            try:
                cls._swiggy_tools = await client.get_tools()
                return cls._swiggy_tools

            except HTTPError as e:
                logger.error(f"HTTP error occurred while fetching Swiggy tools: {e}")
                return []
            except Exception as e:
                logger.error(f"Error fetching Swiggy tools: {e}")
                raise e
    @classmethod
    def update_token(cls, new_token: str):
        """Updates the access token and invalidates the tool cache.

        Args:
            new_token (str): The new bearer token for authentication.
        """
        cls.TOKEN = new_token
        cls.HEADERS = {"Authorization": f"Bearer {cls.TOKEN}"}
        cls._instamart_tools = None
        cls._swiggy_tools = None
        cls._transport = os.getenv("MCP_TRANSPORT", "streamable_http")
