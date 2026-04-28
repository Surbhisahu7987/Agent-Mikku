import logging


logger = logging.getLogger("rag_agent")
logger.setLevel(logging.INFO)

# Example handler setup
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
    