
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from python_template.models.item import Item
from python_template.schemas.item import ItemCreate, ItemUpdate


async def get_items(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> tuple[list[Item], int]:
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(Item))
    total = count_result.scalar_one()

    # Get items
    result = await db.execute(select(Item).offset(skip).limit(limit))
    items = result.scalars().all()

    return items, total


async def get_item(db: AsyncSession, item_id: int) -> Item | None:
    result = await db.execute(select(Item).where(Item.id == item_id))
    return result.scalar_one_or_none()


async def create_item(db: AsyncSession, item: ItemCreate) -> Item:
    db_item = Item(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def update_item(db: AsyncSession, item_id: int, item: ItemUpdate) -> Item | None:
    db_item = await get_item(db, item_id)
    if db_item:
        for key, value in item.model_dump(exclude_unset=True).items():
            setattr(db_item, key, value)
        await db.commit()
        await db.refresh(db_item)
    return db_item


async def delete_item(db: AsyncSession, item_id: int) -> bool:
    db_item = await get_item(db, item_id)
    if db_item:
        await db.delete(db_item)
        await db.commit()
        return True
    return False
