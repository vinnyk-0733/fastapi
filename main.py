from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Depends
from models import Product
from fastapi.middleware.cors import CORSMiddleware
from database import session,engine
import database_models
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        database_models.Base.metadata.create_all(bind=engine)
        init_db()
    except Exception as e:
        print(f"Warning: Could not connect to default database on startup: {e}")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"]
)



@app.get("/")
def greet():
    return "welcome to fastapi"


products = [
    Product(id=1,name="phone",description="budget phone",price=99,quantity= 10),
    Product(id=2,name="laptop", description="gaming laptop",price=999,quantity= 6),
    Product(id=3,name="Pen",description="Blue ink pen",price=10,quantity=100),
    Product(id=4,name="table",description='Marble table',price=4000,quantity=4)
]


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()
        

def init_db():
    db = session()
    try:
        count = db.query(database_models.Product).count()
        
        if count == 0:
            for product in products:
                db.add(database_models.Product(**product.model_dump()))

            db.commit()
    finally:
        db.close()

    

@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    db_products = db.query(database_models.Product).all()
    return db_products


@app.get("/products/{id}")
def get_product_id(id:int,db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id==id).first()
    if db_product:
        return db_product
    
    return "Product not found"


@app.post("/products")
def add_product(product: Product,db: Session = Depends(get_db)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return product
            

@app.put("/products/{id}")
def update_product(id: int, product:Product,db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id==id).first()
    if db_product:
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        return "Product updated"
    else:
        return "Product not found"  

@app.delete("/products/{id}")    
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return "Product deleted"
    else:
        return "Product not found"


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)