import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()
class ModelProvider(Enum):
    GOOGLE = ("google", "GOOGLE_API_KEY")
    OPENAI = ("openai", "OPENAI_API_KEY")
    ANTHROPIC = ("anthropic", "ANTHROPIC_API_KEY")

    def __init__(self, provider_name: str, env_var: str):
        self.provider_name = provider_name
        self.env_var = env_var
    @property
    def token(self) -> str:
        """
        Encapsulates the token retrieval logic inside the Enum.
        """
        val = os.getenv(self.env_var)
        if not val:
            raise ValueError(f"Missing environment variable: {self.env_var}")
        return val
    


