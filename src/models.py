from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)


class ItemResponse(BaseModel):
    item_id: int
    name: str
    price: float
    q: str | None = None
