from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services.llm_service import LLMService
from services.product_service import ProductService

app = FastAPI(title="AI Product Recommendation API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

product_service = ProductService()
llm_service = LLMService()

class LikedProduct(BaseModel):
    id: str
    name: str
    category: str
    brand: Optional[str] = None
    price: Optional[float] = None

class UserPreferences(BaseModel):
    priceRange: str = "all"
    categories: List[str] = []
    brands: List[str] = []

class RecommendationRequest(BaseModel):
    preferences: UserPreferences
    likedProducts: List[LikedProduct] = []
    browsing_history: List[str] = []  # For backward compatibility with test script

PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'products.json')

try:
    with open(PRODUCTS_FILE, 'r') as f:
        products_data = json.load(f)
except Exception as e:
    print(f"Error loading product data: {e}")
    products_data = []

@app.get("/api/products")
async def get_products():
    """Return the full product catalog"""
    products = product_service.get_all_products()
    return products

@app.post("/api/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """Generate personalized product recommendations based on user preferences and liked products"""
    try:
        # Convert to dict ero
        user_preferences = {
            "priceRange": request.preferences.priceRange,
            "categories": request.preferences.categories,
            "brands": request.preferences.brands
        }
        
        # Get all products
        all_products = product_service.get_all_products()
        
        # Handle both liked products and browsing history
        liked_products = request.likedProducts
        
        if not liked_products and request.browsing_history:
            product_map = {p.id: p for p in all_products}
            for product_id in request.browsing_history:
                if product_id in product_map:
                    product = product_map[product_id]
                    liked_products.append(LikedProduct(
                        id=product.id,
                        name=product.name,
                        category=product.category,
                        brand=product.brand,
                        price=product.price
                    ))
        
        # Generate recommendations
        recommendations = await llm_service.generate_recommendations(
            user_preferences,
            liked_products,
            all_products
        )
        
        return recommendations
    
    except Exception as e:
        print(f"Error in recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return {
        "error": str(exc),
        "message": "An error occurred while processing your request"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)