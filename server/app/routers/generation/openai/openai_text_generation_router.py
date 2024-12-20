import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import asyncio

from typing import List, Any, Dict, Type, Optional
from pydantic import BaseModel, Field
from server.app.config.settings import Settings
from server.app.clients.openai.openai_client import OpenAIClient
from server.app.clients.anthropic.anthropic_client import AnthropicClient
from server.app.db.base import async_session_maker
from server.app.models.generation.openai_model import OpenaiModel
from server.app.models.generation.anthropic_model import AnthropicModel
from server.app.models.generation.generation_request import GenerationRequest
from server.app.models.generation.success_generation_model import SuccessGenerationModel
from sqlalchemy import select
from server.app.models.usercontext.user_context import UserContextModel
from server.app.utils.auth import auth
from server.app.services.gripsbox_service import add_gripsbox_content_to_llm_context
from server.app.models.users.user import User
import json
router = APIRouter()
settings = Settings()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
openai_client = OpenAIClient(api_key=settings.get("default").get("API_KEY_OPEN_AI"))
anthropic_client = AnthropicClient(api_key=settings.get("default").get("API_KEY_ANTHROPIC"))

registered_methods = ['fetch_completion', 'chat_completion']
clients = {
    'openai': openai_client,
    'anthropic': anthropic_client,
}

MODEL_CLASS_MAP: Dict[str, Type] = {
    "openai": OpenaiModel,
    "anthropic": AnthropicModel,
}


class ModelNotFoundException(Exception):
    def __init__(self, platform: str):
        self.platform = platform
        super().__init__(f"Model class for platform '{platform}' not found")


class ModelConfig(BaseModel):
    platform: str = Field(..., example="openai", description="The AI platform to use.")
    model: str = Field(..., example="gpt-3.5-turbo", description="The specific model to use.")
    temperature: float = Field(0.7, ge=0, le=1, example=0.7, description="Controls randomness in output.")
    max_tokens: int = Field(100, gt=0, example=100, description="Maximum number of tokens to generate.")
    model_id: Optional[str] = Field(None, description="Unique identifier for the model (if applicable).")
    object: Optional[str] = Field(None, description="Object type (if applicable).")


async def get_db():
    async with async_session_maker() as session:
        yield session


def get_model_class(platform: str):
    model_class = MODEL_CLASS_MAP.get(platform)
    if model_class is None:
        raise ModelNotFoundException(platform)
    return model_class


def validate_models_and_clients(models: List[ModelConfig], method_name: str) -> List[Any]:
    valid_models = []
    for model_data in models:
        platform = model_data.platform
        try:
            model_class = get_model_class(platform)
        except ModelNotFoundException as e:
            logger.error(str(e))
            raise HTTPException(status_code=400, detail=str(e))

        platform_client = clients.get(platform)
        if not platform_client:
            raise HTTPException(status_code=400, detail=f"Client for platform '{platform}' not supported")

        if not hasattr(platform_client, method_name):
            raise HTTPException(status_code=400, detail=f"Method '{method_name}' not found for platform '{platform}'")

        model_dict = model_data.model_dump(exclude_none=True)

        if platform == "openai":
            if not model_dict.get("id"):
                if model_dict.get("model_id"):
                    model_dict["id"] = model_dict["model_id"]
                elif model_dict.get("model"):
                    model_dict["id"] = model_dict["model"]
                else:
                    raise HTTPException(status_code=400,
                                        detail="Either 'model_id' or 'model' must be provided to set 'id' for OpenAI models.")

        if platform == "anthropic":
            if not model_dict.get("id"):
                if model_dict.get("model_id"):
                    model_dict["id"] = model_dict["model_id"]
                elif model_dict.get("model"):
                    model_dict["id"] = model_dict["model"]
                else:
                    raise HTTPException(status_code=400,
                                        detail="Either 'model_id' or 'model' must be provided to set 'id' for Anthropic models.")

        try:
            model_instance = model_class(**model_dict)
        except ValueError as e:
            logger.error(f"Error creating model instance: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid model configuration for {platform}: {str(e)}")

        valid_models.append((model_instance, platform_client, getattr(platform_client, method_name)))

    return valid_models


async def get_user_context(thread_id: int = 1) -> str:
    async for session in get_db():  # Correctly retrieve the session from the async generator
        result = await session.execute(
            select(UserContextModel)
            .where(UserContextModel.thread_id == thread_id)
            .order_by(UserContextModel.created.asc())
        )
        user_contexts = result.scalars().all()

        # Extract context_data, parse JSON if needed, and get 'content' values
        content_list = []
        for uc in user_contexts:
            context_data = uc.context_data  # Assuming `uc.context_data` is already a dict
            if isinstance(context_data, str):
                # If context_data is a JSON string, parse it
                context_data = json.loads(context_data)

            # Process context_data to extract 'content'
            if isinstance(context_data, list):  # Assuming it's a list of dicts
                for data_item in context_data:
                    completion = data_item.get("completion", {})
                    choices = completion.get("choices", [])
                    for choice in choices:
                        content = choice.get("message", {}).get("content")
                        if content:
                            content_list.append(content)

        # Combine all content into a single string
        combined_context = " ".join(content_list)

        logger.debug(f"userContext start: {content_list}")
        logger.debug(f"userContext end")

        return combined_context



@router.post(
    "/stream/openai",
    response_model=SuccessGenerationModel,
    tags=["generation"],
    summary="Stream OpenAI or Anthropic Model Generation",
    description=(
            "This endpoint streams AI-generated content based on the provided prompt and model configurations. "
            "It supports models from OpenAI and Anthropic platforms. "
            "The request must specify the platform and model configuration in the `models` field. "
            "The method specified in the `method_name` field will be invoked on the selected models. "
            "If the configuration is invalid or the platform is not supported, a `400 Bad Request` error is raised."
    ),
)
@router.post(
    "/stream/openai",
    response_model=SuccessGenerationModel,
    tags=["generation"],
    summary="Stream OpenAI or Anthropic Model Generation",
    description=(
        "This endpoint streams AI-generated content based on the provided prompt and model configurations. "
        "It supports models from OpenAI and Anthropic platforms. "
        "The request must specify the platform and model configuration in the `models` field. "
        "The method specified in the `method_name` field will be invoked on the selected models. "
        "If the configuration is invalid or the platform is not supported, a `400 Bad Request` error is raised."
    ),
)
async def stream_route(request: GenerationRequest, user: User = Depends(auth)):
    """
    Stream AI-generated content based on the provided prompt and model configurations.

    - **request**: A `GenerationRequest` object containing the models, method name, and other parameters for generation.
    - **db**: Database session dependency.

    This endpoint validates the model configurations and method name, then streams the generated content
    as a JSON response. It supports concurrent model generation and handles errors related to invalid configurations.

    **Returns**: A streaming JSON response with the generation result.
    """
    logger.info("Incoming request to /stream/openai:")
    logger.info(request.model_dump_json())  # Use model_dump_json for logging
    logger.info("=" * 50)

    # Fetch user context from the database
    user_context = await get_user_context(thread_id=1)

    try:
        gripsbox_context_messages = await add_gripsbox_content_to_llm_context(user)
        # Safely join content messages
        gripsbox_content = " ".join([msg.content for msg in gripsbox_context_messages])

        print(f"--------------------------------------")
        print(f"Gripsbox content: {gripsbox_content}")

    except Exception as e:
        # Log the error if necessary
        print(f"Error adding Gripsbox content: {e}")
        gripsbox_content = ""

    # Combine user context and Gripsbox content into a single context
    combined_context = user_context + " " + gripsbox_content


    # Validate models and clients
    valid_models = validate_models_and_clients(request.models, request.method_name)

    async def generate():
        tasks = []

        for model, client, method in valid_models:
            # Pass the combined context as a parameter to fetch_completion
            async_task = method(model, request.prompt, request.id, context=combined_context)
            task = asyncio.create_task(async_task)
            tasks.append(task)

        for completed_task in asyncio.as_completed(tasks):
            async_gen = await completed_task
            async for result in async_gen:
                if isinstance(result, bytes):
                    result = result.decode('utf-8')

                # Deserialize using Pydantic model's model_validate
                success_model = SuccessGenerationModel.model_validate(json.loads(result))
                # Serialize using model_dump_json
                yield success_model.model_dump_json().encode('utf-8') + b'\n'

    return StreamingResponse(generate(), media_type='application/json')

