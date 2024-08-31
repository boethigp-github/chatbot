import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from server.app.models.usercontext.user_context import UserContextModel
from server.app.models.usercontext.usercontext_post_request import UserContextPostRequestModel
from server.app.models.usercontext.usercontext_response import UserContextResponseModel
from ..db.base import async_session_maker
from typing import List  # Import List from typing
# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get the database session
async def get_db():
    async with async_session_maker() as session:
        yield session

@router.get("/usercontext", tags=["usercontext"], response_model=List[UserContextResponseModel])
async def get_user_contexts(user_id: str, thread_id: int, db: AsyncSession = Depends(get_db)):
    # Query the database for user contexts with the specified user_id and thread_id
    result = await db.execute(
        select(UserContextModel).where(
            UserContextModel.user_id == user_id,
            UserContextModel.thread_id == thread_id
        )
    )
    user_contexts = result.scalars().all()

    if not user_contexts:
        raise HTTPException(status_code=404, detail=f"No user contexts found for user_id {user_id} and thread_id {thread_id}")

    return [user_context.to_dict() for user_context in user_contexts]

@router.post("/usercontext", tags=["usercontext"], response_model=UserContextResponseModel)
async def save_user_context(user_context: UserContextPostRequestModel, db: AsyncSession = Depends(get_db)):
    logger.debug(f"Received request to save user context: {user_context.model_dump()}")

    try:
        # Check if a UserContext with the same user_id and thread_id already exists
        result = await db.execute(
            select(UserContextModel).where(
                UserContextModel.user_id == user_context.user_id,
                UserContextModel.thread_id == user_context.thread_id
            )
        )
        existing_user_context = result.scalars().first()

        if existing_user_context:
            logger.info(f"Updating existing user context with user_id {user_context.user_id} and thread_id {user_context.thread_id}")
            for field, value in user_context.dict(exclude_unset=True).items():
                setattr(existing_user_context, field, value)
            await db.commit()
            await db.refresh(existing_user_context)
            return UserContextResponseModel.from_orm(existing_user_context)
        else:
            logger.info(f"Creating new user context with user_id {user_context.user_id} and thread_id {user_context.thread_id}")
            new_user_context = UserContextModel(**user_context.model_dump())
            db.add(new_user_context)
            await db.commit()
            await db.refresh(new_user_context)
            return UserContextResponseModel.from_orm(new_user_context)

    except Exception as e:
        logger.error(f"Error occurred while saving user context: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.delete("/usercontext/{user_context_id}", tags=["usercontext"])
async def delete_user_context(user_context_id: int, db: AsyncSession = Depends(get_db)):
    try:
        logger.debug(f"delete_user_context and user_context_id {user_context_id}")
        # Fetch the UserContext by primary key using db.get
        user_context = await db.get(UserContextModel, user_context_id)

        if not user_context:
            raise HTTPException(status_code=404, detail=f"User context with id {user_context_id} not found")

        await db.delete(user_context)
        await db.commit()

        return {"status": "User context deleted successfully"}

    except Exception as e:
        logger.error(f"Error occurred while deleting user context: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")




