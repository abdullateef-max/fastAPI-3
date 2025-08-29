from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models.database import Product, get_session
from utils.auth import get_current_user
from typing import Any, Dict, List
from datetime import datetime
import json

router = APIRouter(prefix="/cart", tags=["cart"])

# In-memory cart storage (in production, use database)
user_carts: Dict[int, List[Dict]] = {}

@router.post("/add")
def add_to_cart(
    product_id: int, 
    quantity: int, 
    current_user: Any = Depends(get_current_user),  # Changed from User to Any
    session: Session = Depends(get_session)
):
    # Get product
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Initialize user cart if not exists
    if current_user.id not in user_carts:
        user_carts[current_user.id] = []
    
    # Check if product already in cart
    cart = user_carts[current_user.id]
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            break
    else:
        cart.append({"product_id": product_id, "quantity": quantity})
    
    return {"message": "Product added to cart", "cart": cart}

@router.post("/checkout")
def checkout(
    current_user: Any = Depends(get_current_user),  # Changed from User to Any
    session: Session = Depends(get_session)
):
    if current_user.id not in user_carts or not user_carts[current_user.id]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    cart = user_carts[current_user.id]
    total_amount = 0
    order_items = []
    
    # Process each item in cart
    for item in cart:
        product = session.get(Product, item["product_id"])
        if not product:
            continue
        
        if product.stock < item["quantity"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock for {product.name}"
            )
        
        # Update stock
        product.stock -= item["quantity"]
        session.add(product)
        
        # Calculate total
        item_total = product.price * item["quantity"]
        total_amount += item_total
        
        order_items.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": item["quantity"],
            "price": product.price,
            "total": item_total
        })
    
    # Create order
    order = {
        "user_id": current_user.id,
        "username": current_user.username,
        "items": order_items,
        "total_amount": total_amount,
        "timestamp": str(datetime.now())
    }
    
    # Save to orders.json
    try:
        with open("orders.json", "r") as f:
            orders = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        orders = []
    
    orders.append(order)
    
    with open("orders.json", "w") as f:
        json.dump(orders, f, indent=2)
    
    # Clear cart
    user_carts[current_user.id] = []
    
    session.commit()
    
    return {
        "message": "Order placed successfully",
        "order": order,
        "total_amount": total_amount
    }