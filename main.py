import os
import asyncio
import base64
from typing import Optional
import mlflow
from colorama import Fore, Style, init
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.postgres import PostgresStore
from agents.master_agent import MasterAgent
from agents.middleware.middlewares import get_state
from state.states import CustomAgentState
from schema.model_provider import ModelProvider
from utils.logger import logger
from utils.common import get_db_uri
load_dotenv()

mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
mlflow.set_experiment(os.environ.get("MASTER_MLFLOW_EXP_NAME", "Master Agent"))
mlflow.langchain.autolog()

# Initialize colorama for clean CLI visuals
init(autoreset=True)

class SwiggyAgentCLI:
    def __init__(self, agent):
        self.agent = agent
        self.session_active = True

    def _format_user_input(self, text: str, image_path: Optional[str] = None):
        """
        Formats the input to match the working 'messages' structure.
        """
        if not image_path:
            formatted_query = text 
        
        # If there is an image, we must use the content block list
        # Ensure your BaseAgent/Executor can handle this list format
        else:
            formatted_query = [
                {"type": "text", "text": text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{self._encode_image(image_path)}"}
                }
            ]

        return formatted_query

    def _encode_image(self, image_path: str) -> str:
        """
        Converts an image file to a base64 string.
        """
        try:
            with open(image_path, "rb") as image_file:
                # Read the binary data and encode it
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except FileNotFoundError:
            logger.info(f"\n[!] Error: The file {image_path} was not found.")
            return ""
        except Exception as e:
            logger.error(f"\n[!] Error encoding image: {e}")
            return ""

    async def start(self):
        """
        Starts the CLI session. 

        T
        """
        print(Fore.GREEN + Style.BRIGHT + "=== Swiggy Master Orchestrator CLI ===")
        print("Type 'exit' to quit. Use 'img:path/to/image.jpg message' for multimodal queries.")
        
        while self.session_active:
            try:
                user_input = input(Fore.YELLOW + "\nYou: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    self.session_active = False
                    print(Fore.MAGENTA + "Goodbye!")
                    break

                # Handle multimodal trigger
                image_path = None
                text_query = user_input
                if user_input.startswith("img:"):
                    parts = user_input.split(" ", 1)
                    image_path = parts[0].replace("img:", "")
                    text_query = parts[1] if len(parts) > 1 else "Identify this food."

                # Send to agent
                print(Fore.BLUE + "\n[*] Thinking...")
                # Note: Replace '.invoke' with your agent's specific call method
                input_str = self._format_user_input(text_query, image_path)
                # print((input_str.content))

                response = await self.agent.generate_response(input_str)
                print(Fore.GREEN + response)
                    
            except KeyboardInterrupt:
                logger.info(Fore.MAGENTA + "\nSession ended by user.")
                break
            except Exception as e:
                logger.error(Fore.RED + f"\n[!] An error occurred: {e}")



# --- Execution Entry Point ---
if __name__ == "__main__":
    # Import your master agent factory here
    # from agents.master_agent import get_master_agent
    
    async def main():
        model_name = os.environ.get("MASTER_AGENT_MODEL", "gpt-4")
        model_provider = os.environ.get("MASTER_AGENT_MODEL_PROVIDER", "google_genai")
        checkpointer = InMemorySaver()
        # store = 
        master_agent = MasterAgent(model_name=model_name,
                               model_provider=ModelProvider(model_provider),
                               agent_config={"checkpointer": checkpointer,
                                             "state_schema": CustomAgentState,
                                            #  "middleware": [get_state]

                                             },                                          
                                             )
    
        cli = SwiggyAgentCLI(master_agent)
        await cli.start()

    asyncio.run(main())