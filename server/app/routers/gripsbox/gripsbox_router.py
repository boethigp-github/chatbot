import json
from fastapi import HTTPException
from sqlalchemy.future import select
from server.app.models.gripsbox.gripsbox_model import Gripsbox
from server.app.models.users.user import User
from typing import List
from server.app.config.settings import Settings
from uuid import UUID
import logging
from fastapi import APIRouter, Depends, status, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.services.gripsbox_service import create_gripsbox_service
from server.app.models.gripsbox.gripsbox_post_response import GripsboxPostResponseModel
from server.app.utils.auth import auth
from server.app.db.get_db import get_db
from server.app.models.gripsbox.gripsbox_post_request import GripsboxPostRequestModel

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()
settings = Settings()

# Load allowed file extensions from environment variable
allowed_file_extensions_str = settings.get("default").get("ALLOWED_FILE_EXTENSIONS")
ALLOWED_FILE_EXTENSIONS = json.loads(allowed_file_extensions_str)

@router.get("/gripsbox", response_model=List[GripsboxPostResponseModel], tags=["gripsbox"])
async def get_gripsbox(db: AsyncSession = Depends(get_db),  _: str = Depends(auth)):
    try:
        result = await db.execute(select(Gripsbox).order_by(Gripsbox.created.desc()))
        gripsbox_list = result.scalars().all()
        return gripsbox_list
    except Exception as e:
        logger.error(f"Error retrieving gripsbox: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.post("/gripsbox", response_model=GripsboxPostResponseModel, status_code=status.HTTP_201_CREATED, tags=["gripsbox"])
async def create_gripsbox(
    name: str = Form(...),
    size: int = Form(...),
    type: str = Form(...),
    active: bool = Form(...),
    tags: str = Form(...),
    models: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth)
):
    logger.info(f"Gripsbox user info: username={user.username}, uuid={user.uuid}")

    tags_list = json.loads(tags)
    models_list = json.loads(models)
    # Prepare the input data for validation
    data = {
        "name": name,
        "size": size,
        "type": type,
        "active": active,
        "tags": tags_list,
        "models": models_list
    }

    # Validate using model_validate without try-except
    gripsbox_data = GripsboxPostRequestModel.model_validate(data)

    # Pass the validated request model and other necessary arguments to the service
    new_gripsbox = await create_gripsbox_service(
        file=file,
        gripsbox_post_data=gripsbox_data,
        db=db,
        user=user
    )

    return GripsboxPostResponseModel.from_orm(new_gripsbox)


@router.delete("/gripsbox/{id}", tags=["gripsbox"])
async def delete_gripsbox(id: UUID, db: AsyncSession = Depends(get_db), _: str = Depends(auth)):
    gripsbox = await db.get(Gripsbox, id)
    if gripsbox:
        await db.delete(gripsbox)
        await db.commit()
        logger.info(f"Gripsbox deleted successfully: id={id}")
        return {"status": "Gripsbox deleted successfully"}
    else:
        logger.warning(f"Gripsbox not found: id={id}")
        raise HTTPException(status_code=404, detail=f"Gripsbox with id {id} not found")
