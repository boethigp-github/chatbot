from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from server.app.config.settings import Settings
from server.app.clients.openai.openai_client import OpenAIClient
from server.app.clients.anthropic.anthropic_client import AnthropicClient
from server.app.clients.googleai.google_ai_client import GoogleAICLient
import logging
from server.app.models.models.models_get_response import ModelGetResponseModel  # Your provided path

# Initialize the logger
logger = logging.getLogger("models_router")
settings = Settings()  # Initialize settings

# Initialize the router
router = APIRouter()


# Define the function to get cache from the request's application state
def get_cache(request: Request):
    return request.app.state.cache


@router.get("/models", response_model=List[ModelGetResponseModel], tags=["models"])
async def get_models(cache=Depends(get_cache)):
    """
    Retrieves available models from OpenAI and Anthropic,
    merges them into a single list, and returns them as a JSON response.
    The results are cached for 300 seconds (5 minutes).
    """
    try:
        # Check if the result is in the cache
        cached_models = cache.get("models_list")
        if cached_models:
            logger.debug("Cache hit: Returning cached models list")
           # return cached_models  # The response model handles the serialization

        # Retrieve models from OpenAI and potentially other sources
        openai_models = OpenAIClient(api_key=settings.get("default").get("API_KEY_OPEN_AI")).get_available_models()
        anthropic_models = AnthropicClient(api_key=settings.get("default").get("API_KEY_ANTHROPIC")).get_available_models()
        google_ai_models = GoogleAICLient(api_key=settings.get("default").get("API_KEY_GOOGLE_AI")).get_available_models()

        # Merge and cache the models
        all_models = openai_models + anthropic_models + google_ai_models
        cache.set("models_list", all_models, expire=300)
        logger.debug("Cache miss: Retrieved and cached new models list")

        return all_models
    except Exception as e:
        logger.error(f"Error retrieving models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving models: {str(e)}")
