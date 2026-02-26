from pydantic import BaseModel, Field, create_model
from typing import Annotated, Any, Dict, Type, Literal
from fastapi import FastAPI, Depends, Header, Path, HTTPException, status
from datetime import date

app = FastAPI()


Category_definations = {
    1: {"name":"Laptop",
         "fields":{"cpu_type": (str,...), "ram_gb":(int,...)}},
    2: {"name":"T-shirts",
        "fields":{"colour":(str,...), "size":(Literal['S','M','L','XL'], ...)}},
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

PRODUCT_DATABASES = {
    101: {"category_id": 1, "sku":"DELL-XPS-15", "price": 1899.00, "attributes":{"cpu_type":"Intel i9","ram_gb":256}},
    102: {"category_id": 2, "sku":"PLAIN-WHITE-T", "price": 500.00, "attributes":{"colour":"Red","size":"XL"}},
    103: {"category_id": 3, "sku":"CNC-MILL-01", "price": 75000.00, "attributes":{"voltage": 220,"warranty_expires_on":240506}}
}

@app.get("/products/{product_id}")
async def get_product(product_id):
    product_data = PRODUCT_DATABASES[int(product_id)]
    if not product_id:
        raise HTTPException(Status_code=404, detail="Product does not exist duh!")
    category_id = product_data["category_id"]
    ResponseModel = get_product_model_For_Category(category_id)

    Response_Data = {
        "sku": product_data["sku"],
        "price":product_data["price"],
        **product_data["attributes"]
    }

    try:
        return ResponseModel(**Response_Data)
    except Exception as err:
        raise HTTPException(status_code=422, detail=f"{err}")
    

@app.get("/products", response_model = list[Dict[str, Any]])
async def get_all_products():
    return list(PRODUCT_DATABASES.values())