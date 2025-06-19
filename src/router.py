from fastapi import APIRouter, Depends, Path, Query
from .auth import verify_token
from .models import Item, ItemResponse

router = APIRouter()


@router.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application!"}


@router.get("/items/{item_id}", response_model=ItemResponse)
async def read_item(
    item_id: int = Path(..., gt=0),
    q: str | None = Query(None, max_length=50),
    _: str = Depends(verify_token),
):
    item = {"name": f"item{item_id}", "price": 100.0}
    return ItemResponse(item_id=item_id, name=item["name"], price=item["price"], q=q)


@router.post("/items", response_model=ItemResponse)
async def create_item(item: Item, _: str = Depends(verify_token)):
    return ItemResponse(item_id=1, name=item.name, price=item.price)
