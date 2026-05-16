from enum import Enum

class ModelProvider(Enum):
    GOOGLE = "google_genai" #, "GOOGLE_API_KEY"
    OPENAI = "openai" # "OPENAI_API_KEY"
    ANTHROPIC = "anthropic" #"ANTHROPIC_API_KEY"
    OLLAMA = "ollama" 
    HF = "huggingface" #"HUGGINGFACE_API_KEY"
    


