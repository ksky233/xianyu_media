from langchain_dev_utils.chat_models import batch_register_model_provider
from dotenv import load_dotenv

load_dotenv()

batch_register_model_provider([
    {"provider_name": "dashscope", "chat_model": "openai-compatible"}
])