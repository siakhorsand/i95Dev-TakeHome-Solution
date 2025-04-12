import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', "") 
MODEL_NAME = "gpt-3.5-turbo" 
MAX_TOKENS = 1000 
TEMPERATURE = 0.7  

DATA_PATH = os.path.join(BACKEND_DIR, "data", "products.json")

config = {
    'OPENAI_API_KEY': OPENAI_API_KEY,
    'MODEL_NAME': MODEL_NAME,
    'MAX_TOKENS': MAX_TOKENS,
    'TEMPERATURE': TEMPERATURE,
    'DATA_PATH': DATA_PATH
}

LLM_CONFIG = {
    'api_key': OPENAI_API_KEY,
    'model': MODEL_NAME,
    'max_tokens': MAX_TOKENS,
    'temperature': TEMPERATURE,
    'use_mock_api': False # change to use mock api
}