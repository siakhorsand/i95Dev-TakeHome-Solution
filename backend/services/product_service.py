import json
from config import config
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

from services.llm_service import Product

class ProductService:
    def __init__(self):
        self.data_path = config['DATA_PATH']
        self.raw_products = self._load_products()
        self.products = self._convert_to_product_objects()
    
    def _load_products(self):
        try:
            with open(self.data_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading product data: {str(e)}")
            return []
    
    def _convert_to_product_objects(self):
        product_objects = []
        for p in self.raw_products:
            product_objects.append(Product(
                id=p.get('id'),
                name=p.get('name'),
                description=p.get('description', ''),
                price=p.get('price', 0),
                category=p.get('category', ''),
                brand=p.get('brand', ''),
                image=p.get('image'),
                rating=p.get('rating')
            ))
        return product_objects
    
    def get_all_products(self):
        return self.products
    
    def get_product_by_id(self, product_id):
        for product in self.products:
            if product.id == product_id:
                return product
        return None
    
    def get_products_by_category(self, category):
        return [p for p in self.products if p.category == category]