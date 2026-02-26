from pydantic import BaseModel, Field, create_model
from typing import Annotated, Any, Dict, Type
from fastapi import FastAPI, Depends, Header, Path, HTTPException, status
from datetime import date

app = FastAPI()

# class ItemCreate(BaseModel):
#     name: str
#     price: float | None = None

# async def get_db_session():
#     print("DB session > start")
#     session = {"data": {1:{"name":"Namita"}, 2:{"name":"Item_two"}}}
#     try:
#         yield session
#     finally:
#         print("DB session < teardown")

# Dbsession = Annotated[dict, Depends(get_db_session)]   


# async def get_user(token: Annotated[str | None, Header()]=None):
#     print("Checking auth..")
#     return {"username": "Test_user"}

# CurrentUser = Annotated[dict, Depends(get_user)]

# @app.get("/item/{item_id}")
# async def read_item(item_id: Annotated[int, Path(ge=1)], db: Dbsession):
#     print("reading items")
#     if item_id not in db["data"]:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item is not present")
#     return {"id": item_id, **db['data'][item_id]}


# @app.post("/item")
# async def create_item(
#     item: ItemCreate,
#     db: Dbsession,
#     user: CurrentUser
#     ):
#     print(f"User {user['username']} creating item")
#     new_id = max(db["data"].keys() or [0]) + 1
#     db["data"][new_id] = item.model_dump()
#     return {"id": new_id, **item.model_dump()}

Category_definations = {
    1: {"name":"Laptop",
         "fields":{"cpu_type": (str,...), "ram_gb":(int,...)}},
    2: {"name":"T-shirts",
        "fields":{"colour":(str,...), "size":(str, "M")}},
    3: {"name":"Equipment",
        "fields":{"voltage":(int,...), "warranty_Expires_on":(date, ...)}}
}

#creating methods which can generate dynamic model

def get_product_model_For_Category(category_id: int) -> Type[BaseModel]:
    category = Category_definations.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Product category {category_id} not found.")
    
    #Base fields common to all products

    base_fields = {
        "sku": (str, ...),
        'price':(float, Field(..., gt=0))
    }
    
    #adding category specific fields and combining all
    all_fields = {**base_fields, **category["fields"]}

    #building Model to build class

    ProductModel = create_model(
        f'Dynamic{category["name"]}Model',
        **all_fields
    )

    return ProductModel


#Post request
@app.post("/products/{category_id}")
async def create_dynamic_product(
        category_id: int,
        request_body: Dict[str, Any]
):
   Model = get_product_model_For_Category(category_id)
   try:
       validate_product = Model(**request_body)
   except Exception as err:
       raise HTTPException(status_code=422, detail=err)
   return {
       "message": "Product created successfully",
       "product": validate_product.model_dump()
   }
