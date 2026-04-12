
from math import ceil
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from python_template.api.exceptions import APIError
from python_template.core.logger import logger
from python_template.crud import item as crud_item
from python_template.db.session import get_db
from python_template.schemas import item as schema_item
from python_template.schemas.common import PaginatedResponse

router = APIRouter()


def log_item_creation(item_id: int):
    logger.info(f"Background Task: Item {item_id} created successfully.")


@router.post("/", response_model=schema_item.Item)
async def create_item(
    item: schema_item.ItemCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    db_item = await crud_item.create_item(db=db, item=item)
    background_tasks.add_task(log_item_creation, db_item.id)
    return db_item


@router.get("/", response_model=PaginatedResponse[schema_item.Item])
async def read_items(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    items, total = await crud_item.get_items(db, skip=skip, limit=limit)
    
    page = (skip // limit) + 1
    pages = ceil(total / limit) if total > 0 else 0
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/{item_id}", response_model=schema_item.Item)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    db_item = await crud_item.get_item(db, item_id=item_id)
    if db_item is None:
        raise APIError(message="Item not found", status_code=404)
    return db_item


@router.put("/{item_id}", response_model=schema_item.Item)
async def update_item(
    item_id: int, item: schema_item.ItemUpdate, db: AsyncSession = Depends(get_db)
):
    db_item = await crud_item.update_item(db, item_id=item_id, item=item)
    if db_item is None:
        raise APIError(message="Item not found", status_code=404)
    return db_item


@router.delete("/{item_id}", response_model=bool)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud_item.delete_item(db, item_id=item_id)
    if not success:
        raise APIError(message="Item not found", status_code=404)
    return success
