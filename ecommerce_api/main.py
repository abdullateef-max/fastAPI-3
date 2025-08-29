from fastapi import FastAPI, Request
from routers import users, products, cart, admin
from models.database import create_db_and_tables, get_session, User, Product
from sqlmodel import Session, select
from utils.auth import get_password_hash
import time
import json

app = FastAPI(title="E-Commerce API", version="1.0.0")

# Include routers
app.include_router(users.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(admin.router)

# Add timing middleware directly
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Create a default admin user for testing
    with next(get_session()) as session:
        admin_user = session.exec(select(User).where(User.username == "admin")).first()
        if not admin_user:
            hashed_password = get_password_hash("admin123")
            admin_user = User(
                username="admin", 
                email="admin@example.com", 
                password=hashed_password,
                is_admin=True
            )
            session.add(admin_user)
            session.commit()
        
        # Create some sample products
        products = session.exec(select(Product)).all()
        if not products:
            sample_products = [
                Product(name="Laptop", price=999.99, stock=10),
                Product(name="Smartphone", price=499.99, stock=20),
                Product(name="Headphones", price=99.99, stock=30)
            ]
            for product in sample_products:
                session.add(product)
            session.commit()

@app.get("/")
def read_root():
    return {"message": "Welcome to E-Commerce API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    