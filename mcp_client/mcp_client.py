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
    
    # Caches for initialized tools
    _instamart_tools = None
    _swiggy_tools = None
    _transport = os.getenv("MCP_TRANSPORT", "streamable_http")
    TOKEN = os.getenv("MCP_ACCESS_TOKEN")
    HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

    @staticmethod
    async def im_filter_search_product(request: MCPToolCallRequest,
                                 handler):
        """
        Filter and keep only top 5 products in "data" field

        This method filters the product list received from instamart's
        "search_products" tool and keeps only the top 5 products.
        This help in reduce the token bloat due to multiple irrelevant 
        products received in the tool response by a factor of 5X to 10X.
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
        
        logger.info(f"Calling tool: {request.name}, Request: {request.args}")
        result = await handler(request)

        return result

    @classmethod
    async def get_instamart_tools(cls):
        """Fetches and caches Instamart tools."""
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
                return []
            
    @classmethod
    async def get_swiggy_tools(cls):
        """Fetches and caches Swiggy tools."""
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
                return []

    @classmethod
    def update_token(cls, new_token: str):
        """Wipe cache and update token if credentials change."""
        cls.TOKEN = new_token
        cls.HEADERS = {"Authorization": f"Bearer {cls.TOKEN}"}
        cls._instamart_tools = None
        cls._swiggy_tools = None
        cls._transport = os.getenv("MCP_TRANSPORT", "streamable_http")

