from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models.database import Product, get_session
from utils.auth import get_current_admin
from typing import Any

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
def get_products(session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    return products

@router.post("/")
def create_product(
    name: str, 
    price: float, 
    stock: int, 
    session: Session = Depends(get_session),
    admin: Any = Depends(get_current_admin)  # Changed from User to Any
):
    product = Product(name=name, price=price, stock=stock)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product