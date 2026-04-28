import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

class SwiggyMCPManager:
    _instance = None
    
    # Caches for initialized tools
    _instamart_tools = None
    _food_tools = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SwiggyMCPManager, cls).__new__(cls)
            # Initialize shared config
            cls.TOKEN = os.getenv("SWIGGY_BUILDERS_TOKEN")
            cls.HEADERS = {"Authorization": f"Bearer {cls.TOKEN}"} if cls.TOKEN else {}
        return cls._instance

    async def get_instamart_tools(self):
        """Fetches and caches Instamart tools."""
        if self._instamart_tools is None:
            client = MultiServerMCPClient({
                "instamart": {
                    "transport": "sse",
                    "url": os.environ.get("INSTAMART_MCP_URL", "https://mcp.swiggy.com/instamart/v1"),
                    "headers": self.HEADERS
                }
            })
            self._instamart_tools = await client.get_tools()
        return self._instamart_tools

    async def get_food_delivery_tools(self):
        """Fetches and caches Food Delivery tools."""
        if self._food_tools is None:
            client = MultiServerMCPClient({
                "food": {
                    "transport": "sse",
                    "url": os.environ.get("FOOD_DELIVERY_MCP_URL", "https://mcp.swiggy.com/food/v1"),
                    "headers": self.HEADERS
                }
            })
            self._food_tools = await client.get_tools()
        return self._food_tools

    def update_token(self, new_token: str):
        """Wipe cache and update token if credentials change."""
        self.TOKEN = new_token
        self.HEADERS = {"Authorization": f"Bearer {self.TOKEN}"}
        self._instamart_tools = None
        self._food_tools = None