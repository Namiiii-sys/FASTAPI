from pydantic import BaseModel
from typing import Annotated
from fastapi import FastAPI, Depends, Header, Path, HTTPException, status

app = FastAPI()

class ItemCreate(BaseModel):
    name: str
    price: float | None = None

async def get_db_session():
    print("DB session > start")
    session = {"data": {1:{"name":"Namita"}, 2:{"name":"Item_two"}}}
    try:
        yield session
    finally:
        print("DB session < teardown")

Dbsession = Annotated[dict, Depends(get_db_session)]   


async def get_user(token: Annotated[str | None, Header()]=None):
    print("Checking auth..")
    return {"username": "Test_user"}

CurrentUser = Annotated[dict, Depends(get_user)]

@app.get("/item/{item_id}")
async def read_item(item_id: Annotated[int, Path(ge=1)], db: Dbsession):
    print("reading items")
    if item_id not in db["data"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item is not present")
    return {"id": item_id, **db['data'][item_id]}


@app.post("/item")
async def create_item(
    item: ItemCreate,
    db: Dbsession,
    user: CurrentUser
    ):
    print(f"User {user['username']} creating item")
    new_id = max(db["data"].keys() or [0]) + 1
    db["data"][new_id] = item.model_dump()
    return {"id": new_id, **item.model_dump()}

   
    
   