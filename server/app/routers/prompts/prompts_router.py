import logging
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jsonschema import ValidationError
from server.app.models.prompts.prompts import Prompt
from server.app.db.base import async_session_maker
from server.app.config.settings import Settings
from typing import List
from server.app.models.prompts.prompt_post_response_model import PromptPostResponseModel
from server.app.models.prompts.prompt_post_request_model import PromptPostRequestModel
from uuid import UUID
# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()
settings = Settings()

# Dependency to get the database session
async def get_db():
    async with async_session_maker() as session:
        yield session

@router.get("/prompts", response_model=List[PromptPostResponseModel], tags=["prompts"])
async def get_prompts(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Prompt).order_by(Prompt.created.desc()))
        prompts = result.scalars().all()
        return prompts  # FastAPI will automatically convert SQLAlchemy models to Pydantic models
    except Exception as e:
        logger.error(f"Error retrieving prompts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred {str(e)}")

@router.post("/prompts", response_model=PromptPostResponseModel, status_code=status.HTTP_201_CREATED, tags=["prompts"])
async def create_prompt(prompt: PromptPostRequestModel, db: AsyncSession = Depends(get_db)):
    try:
        # Log the incoming data
        logger.debug(f"Incoming prompt data: {prompt}")

        # Check for existing prompt
        result = await db.execute(
            select(Prompt).filter_by(prompt=prompt.prompt, user=prompt.user)
        )
        existing_prompt = result.scalars().first()

        if existing_prompt:
            logger.info(f"Prompt already exists: {existing_prompt}")
            return PromptPostResponseModel.model_validate(existing_prompt)  # Updated for Pydantic v2

        # Log data to be saved
        logger.debug(f"Creating new prompt with data: {prompt.model_dump()}")

        # Create and save new prompt
        new_prompt = Prompt(**prompt.model_dump())
        db.add(new_prompt)
        await db.commit()
        await db.refresh(new_prompt)

        # Log the newly created prompt
        logger.debug(f"Prompt created successfully: {new_prompt}")

        return PromptPostResponseModel.model_validate(new_prompt)  # Updated for Pydantic v2

    except ValidationError as validation_error:
        logger.error(f"Validation error while creating prompt: {validation_error}")
        raise HTTPException(status_code=400, detail=f"Validation error: {validation_error}")

    except Exception as e:
        logger.error(f"Unexpected error while creating prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred {str(e)}")


@router.delete("/prompts/{uuid}", tags=["prompts"])
async def delete_prompt(uuid: UUID, db: AsyncSession = Depends(get_db)):
    prompt = await db.get(Prompt, uuid)
    if prompt:
        await db.delete(prompt)
        await db.commit()
        logger.info(f"Prompt deleted successfully: id={id}")
        return {"status": "Prompt deleted successfully"}
    else:
        logger.warning(f"Prompt not found: id={id}")
        raise HTTPException(status_code=404, detail=f"Prompt with id {id} not found")
