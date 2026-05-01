import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from utils.logger import logger
load_dotenv()

class SwiggyMCPManager:
    # _instance = None
    
    # Caches for initialized tools
    _instamart_tools = None
    _swiggy_tools = None
    TOKEN = os.getenv("SWIGGY_BUILDERS_TOKEN")
    HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {

    }
    # def __new__(cls):
    #     if cls._instance is None:
    #         cls._instance = super(SwiggyMCPManager, cls).__new__(cls)
    #         # Initialize shared config
            
    #     return cls._instance
    @classmethod
    def get_instamart_tools(cls):
        """Fetches and caches Instamart tools."""
        if cls._instamart_tools is None:
            client = MultiServerMCPClient({
                "instamart": {
                    "transport": "sse",
                    "url": os.environ.get("INSTAMART_MCP_URL", "https://mcp.swiggy.com/instamart/v1"),
                    "headers": cls.HEADERS
                }
            })

            try:
                cls._instamart_tools = client.get_tools()
                return cls._instamart_tools
            except Exception as e:
                logger.error(f"Error fetching Instamart tools: {e}")
                raise e
            
    @classmethod
    def get_swiggy_tools(cls):
        """Fetches and caches Swiggy tools."""
        if cls._swiggy_tools is None:
            client = MultiServerMCPClient({
                "food": {
                    "transport": "sse",
                    "url": os.environ.get("SWIGGY_MCP_URL", "https://mcp.swiggy.com/food/v1"),
                    "headers": cls.HEADERS
                }
            })
            try:
                cls._swiggy_tools = client.get_tools()
            except Exception as e:
                logger.error(f"Error fetching Swiggy tools: {e}")
                raise e
        return cls._swiggy_tools

    @classmethod
    def update_token(cls, new_token: str):
        """Wipe cache and update token if credentials change."""
        cls.TOKEN = new_token
        cls.HEADERS = {"Authorization": f"Bearer {cls.TOKEN}"}
        cls._instamart_tools = None
        cls._swiggy_tools = None
