from fastapi import FastAPI
from models import Product
from database import session,engine
import database_models

database_models.Base.metadata.create_all(bind = engine)

app = FastAPI()

@app.get("/")
def greet():
    return "welcome to fastapi"


products = [
    Product(id=1,name="phone",description="budget phone",price=99,quantity= 10),
    Product(id=2,name="laptop", description="gaming laptop",price=999,quantity= 6),
    Product(id=3,name="Pen",description="Blue ink pen",price=10,quantity=100),
    Product(id=4,name="table",description='Marble table',price=4000,quantity=4)
]

@app.get("/products")
def get_all_products():
    db = session()
    db.query()
    return products


@app.get("/product/{id}")
def get_product_id(id:int):
    for product in products:
        if product.id == id:
            return products[id-1]
    
    return "Product not found"


@app.post("/product")
def add_product(product: Product):
    products.append(product)
    return product
            

@app.put("/product")
def update_product(id: int, product:Product):
    for i in range(len(products)):
        if products[i].id == id:
            products[i] = product
            return "Product updated"
    return "Product not found"  

@app.delete("/product")    
def delete_product(id: int):
    for i in range(len(products)):
        if products[i].id == id:
            del products[i]
            return "Product deleted"
    return "Product not found"