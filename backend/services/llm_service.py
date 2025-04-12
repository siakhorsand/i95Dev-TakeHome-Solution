import json
import random
from openai import OpenAI
import os
import sys

class Product:
    def __init__(self, id, name, description, price, category, brand, image=None, rating=None):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.brand = brand
        self.image = image
        self.rating = rating

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

from config import LLM_CONFIG

# Initialize the OpenAI client with just the API key
class LLMService:
    def __init__(self, config=None):
        self.config = config or LLM_CONFIG
        try:
            self.client = None
            if self.config.get('api_key'):
                self.client = OpenAI(api_key=self.config['api_key'])
        except Exception as e:
            print(f"Warning: OpenAI client initialization failed: {e}")
            # This is fine, we'll use mock recommendations
            self.client = None
    
    async def generate_recommendations(self, preferences, liked_products, products_catalog):
        """Generate personalized product recommendations."""
        try:
            return self._generate_mock_recommendations(preferences, liked_products, products_catalog)
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return {"recommendations": []}
    # generate mock recommendations to fall back on if openai api is down
    def _generate_mock_recommendations(self, preferences, liked_products, products_catalog):
        """Generate mock recommendations based on user preferences and liked products."""
        try:
            liked_product_ids = set(p.id for p in liked_products)
            liked_categories = set(p.category for p in liked_products)
            liked_brands = set(p.brand for p in liked_products)
            
            price_range = preferences.get('priceRange', 'all')
            min_price = 0
            max_price = float('inf')
            if isinstance(price_range, str) and price_range != 'all':
                if '-' in price_range:
                    parts = price_range.split('-')
                    min_price = float(parts[0])
                    max_price = float(parts[1])
                elif '+' in price_range:
                    min_price = float(price_range.rstrip('+'))
                else:
                    try:
                        exact_price = float(price_range)
                        min_price = exact_price * 0.8
                        max_price = exact_price * 1.2
                    except ValueError:
                        pass

            # Get preferred categories from preferences
            preferred_categories = set(preferences.get('categories', []))
            preferred_brands = set(preferences.get('brands', []))

            # by price range
            available_products = []
            for product in products_catalog:
                if product.id in liked_product_ids:
                    continue
                try:
                    price = float(product.price)
                    if price >= min_price and (max_price == float('inf') or price <= max_price):
                        available_products.append(product)
                except (ValueError, AttributeError):
                    continue
            
            if not available_products:
                return {"recommendations": []}

            # different types of recommendations
            preferred_category_products = []
            same_category_products = []
            same_brand_products = []
            complementary_products = []
            other_products = []
            
            complementary_map = {
                'Electronics': ['Accessories', 'Home'],
                'Home': ['Electronics', 'Accessories'],
                'Sports': ['Health', 'Footwear'],
                'Health': ['Sports', 'Electronics'],
                'Beauty': ['Health', 'Accessories'],
                'Footwear': ['Sports', 'Clothing'],
                'Clothing': ['Accessories', 'Footwear'],
                'Accessories': ['Electronics', 'Clothing']
            }
            
            complementary_categories = set()
            for category in liked_categories.union(preferred_categories):
                if category in complementary_map:
                    complementary_categories.update(complementary_map[category])
            
            for product in available_products:
                if preferred_categories and product.category in preferred_categories:
                    preferred_category_products.append(product)
                elif product.category in liked_categories:
                    same_category_products.append(product)
                elif product.brand in liked_brands.union(preferred_brands):
                    same_brand_products.append(product)
                elif product.category in complementary_categories:
                    complementary_products.append(product)
                else:
                    other_products.append(product)
            
            recommendations = []
            
            preferred_limit = 2
            if preferred_categories and preferred_category_products:
                for product in preferred_category_products[:preferred_limit]:
                    liked_ref = next((p for p in liked_products if p.category == product.category), None)
                    if liked_ref:
                        explanation = f"Since you liked {liked_ref.name}, you'll love {product.name} for its {product.description.split(',')[0].lower()}"
                    else:
                        category = next(iter(preferred_categories))
                        explanation = f"Based on your interest in {category}, you'll love {product.name} for its {product.description.split(',')[0].lower()}"
                    
                    recommendations.append({
                        "product": product,
                        "explanation": explanation
                    })
            
            if len(recommendations) < 3 and same_category_products:
                product = same_category_products[0]
                liked_ref = next((p for p in liked_products if p.category == product.category), None)
                if liked_ref:
                    recommendations.append({
                        "product": product,
                        "explanation": f"Since you liked {liked_ref.name}, you'll love {product.name} for its {product.description.split(',')[0].lower()}"
                    })
            
            if len(recommendations) < 3 and same_brand_products:
                product = same_brand_products[0]
                liked_ref = next((p for p in liked_products if p.brand == product.brand), None)
                if liked_ref:
                    recommendations.append({
                        "product": product,
                        "explanation": f"Since you liked {liked_ref.name}, you'll love {product.name} for its premium {product.brand} quality"
                    })
            
            # Add complementary products
            while len(recommendations) < 3 and complementary_products:
                product = complementary_products.pop(0)
                # Find a liked product that this complements
                for liked in liked_products:
                    if liked.category in complementary_map and product.category in complementary_map[liked.category]:
                        recommendations.append({
                            "product": product,
                            "explanation": f"Since you liked {liked.name}, you'll love {product.name} to complement it with {product.description.split(',')[0].lower()}"
                        })
                        break
                else:
                    if liked_products:
                        liked_ref = liked_products[0]
                        recommendations.append({
                            "product": product,
                            "explanation": f"Since you liked {liked_ref.name}, you'll love {product.name} to complement it with {product.description.split(',')[0].lower()}"
                        })
            
            remaining_pools = [preferred_category_products, same_category_products, same_brand_products, complementary_products, other_products]
            for pool in remaining_pools:
                for product in pool:
                    if len(recommendations) >= 3:
                        break
                    if any(r["product"].id == product.id for r in recommendations):
                        continue
                    
                    if liked_products:
                        liked_ref = next(
                            (p for p in liked_products if p.category == product.category),
                            next((p for p in liked_products if p.brand == product.brand), liked_products[0])
                        )
                        recommendations.append({
                            "product": product,
                            "explanation": f"Based on your interest in {liked_ref.category}, you'll love {product.name} for its {product.description.split(',')[0].lower()}"
                        })
                    else:
                        category = product.category
                        recommendations.append({
                            "product": product,
                            "explanation": f"Based on your interests, you'll love {product.name} for its {product.description.split(',')[0].lower()}"
                        })
                
                if len(recommendations) >= 3:
                    break
            
            return {"recommendations": recommendations[:3]}
            
        except Exception as e:
            print(f"Error generating mock recommendations: {e}")
            return {"recommendations": []}
    
    def _filter_products_by_preferences(self, products, preferences):
        """Filter products based on user preferences."""
        filtered_products = []
        
        for product in products:
            # category filter
            if preferences['categories'] and product.category not in preferences['categories']:
                continue
                
            # brand filter
            if preferences['brands'] and product.brand not in preferences['brands']:
                continue
                
            # price range filter
            if preferences['priceRange'] != 'all':
                min_price, max_price = map(float, preferences['priceRange'].split('-'))
                if not (min_price <= product.price <= (max_price if max_price else float('inf'))):
                    continue
            
            filtered_products.append(product)
            
        return filtered_products
    
    def _create_recommendation_prompt(self, preferences, liked_products, catalog):
        """Create a prompt for the LLM to generate recommendations."""
        # liked products info
        liked_items = []
        for p in liked_products:
            liked_items.append(f"- {p.name} (Category: {p.category}, Brand: {p.brand}, Price: ${p.price})")
        
        liked_products_str = "\n".join(liked_items)
        
        # Format preferences
        price_range = preferences.get('priceRange', 'all')
        categories = ", ".join(preferences.get('categories', [])) or "all categories"
        brands = ", ".join(preferences.get('brands', [])) or "all brands"
        
        catalog_items = []
        for p in catalog:
            catalog_items.append({
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "brand": p.brand,
                "price": p.price,
                "description": p.description
            })
        
        # Create the prompt
        prompt = f"""You are an expert AI shopping assistant who personalizes product recommendations.

USER DATA:
1. Liked Products:
{liked_products_str}

2. User Preferences:
   - Price Range: {price_range}
   - Categories: {categories}
   - Brands: {brands}

AVAILABLE PRODUCTS TO RECOMMEND:
{json.dumps(catalog_items, indent=2)}

TASK:
Based on the user's liked products and categorical, brand and price range preferences, recommend 3 products from the available catalog that this user would enjoy most.

PRODUCT RECOMMENDATION RULES:
1. NEVER recommend products the user has already liked
2. Recommend products that match the user's preferences (price range, categories, brands)
3. For variety, recommend products from at least 2 different categories
4. Include a mix of similar products and complementary products
5. Focus on quality matches rather than just matching categories
6. If the user has price preferences, strictly adhere to them
7. Each recommendation MUST include a personalized explanation of why it's being recommended
8. For explanations, ALWAYS use one of these formats EXACTLY:
   - "Since you liked [specific liked product], you'll love [recommended product] for [specific feature/quality]"
   - Only if there are no relevant liked products: "Based on your interest in [category/brand], [recommended product] offers [specific benefit]"
9. Be specific and detailed in explaining why each product fits the user's preferences

RESPONSE FORMAT:
Return a JSON array with exactly 3 product recommendations, each containing:
- product_id: string
- explanation: string (personalized explanation using required format)

Example response format:
[
  {{
    "product_id": "prod123",
    "explanation": "Since you liked Premium Wireless Headphones, you'll love Smart Home Security Camera for its high-definition video quality and seamless smartphone integration."
  }},
  ...
]

Return ONLY the JSON array, no other text."""

        return prompt
    
    async def _call_llm_api(self, prompt):
        """Call OpenAI API with the given prompt."""
        try:
            if not self.client:
                print("OpenAI client not available, cannot make API call")
                return None
                
            messages = [
                {"role": "system", "content": """You are a product recommendation system that MUST follow these exact formats for explanations:
- REQUIRED FORMAT: "Since you liked [Product Name], you'll love [new product] for [specific feature]"
- ONLY if no similar liked products exist: "Based on your interest in [category/brand], you'll love [product] for [specific feature]"

You MUST use the first format ("Since you liked...") if the user has ANY liked products.
NO OTHER FORMATS ARE ALLOWED."""},
                {"role": "user", "content": prompt}
            ]
            
            completion = await self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-3.5-turbo'),
                messages=messages,
                temperature=0.5, # or .6 for more creativity 
                max_tokens=self.config.get('max_tokens', 1000)
            )
            
            # get the response content
            content = completion.choices[0].message.content
            print(f"OpenAI API Response: {content}")  # Debug log
            return content
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            print(f"Prompt used: {prompt}")  # Debug log
            return None  # Let the calling function handle the fallback
    
    def _parse_recommendation_response(self, response_text, products_catalog):
        """Parse the LLM response into product recommendations."""
        if not response_text:
            print("No response from OpenAI API")  # Debug log
            return []
            
        try:
            # Clean up the response text
            json_text = response_text.strip()
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0].strip()
            
            print(f"Cleaned JSON text: {json_text}")  # Debug log
            recommendations_data = json.loads(json_text)
            
            # Map product IDs to actual Product objects and track categories
            product_map = {str(p.id): p for p in products_catalog}
            recommended_categories = set()
            
            recommendations = []
            for item in recommendations_data:
                product_id = str(item.get('product_id'))
                explanation = item.get('explanation', '')
                
                print(f"Processing recommendation for product {product_id}") 
                
                if not product_id or product_id not in product_map:
                    print(f"Skipping product {product_id}: not in catalog")  
                    continue
                
                # Get product
                product = product_map[product_id]
                
                # Skip if we already have too many recommendations from this category
                if product.category in recommended_categories and len(recommended_categories) < 2:
                    print(f"Skipping product {product_id}: too many from category {product.category}") 
                    continue
                
                recommended_categories.add(product.category)
                recommendations.append({
                    "product": product,
                    "explanation": explanation
                })
            
            # If we have fewer than 3 recommendations, try to add more from different categories
            if len(recommendations) < 3:
                for product in products_catalog:
                    if len(recommendations) >= 3:
                        break
                    
                    if (str(product.id) not in [r["product"].id for r in recommendations] and 
                        product.category not in recommended_categories):
                        recommendations.append({
                            "product": product,
                            "explanation": f"Based on your interests, you'll love {product.name} for {product.description.split(',')[0].lower()}"
                        })
                        recommended_categories.add(product.category)
            
            return recommendations[:3]
            
        except Exception as e:
            print(f"Error parsing recommendations: {e}") 
            return [] 
