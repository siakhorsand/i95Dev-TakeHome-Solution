const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Fetch all products from the API
export const fetchProducts = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/products`);
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching products:', error);
    throw error;
  }
};

// Get recommendations based on user preferences and liked products
export const getRecommendations = async (preferences, likes) => {
  try {
    // Convert product IDs to proper product objects if needed
    const likedProducts = Array.isArray(likes) && typeof likes[0] === 'string' 
      ? likes.map(id => ({ id }))
      : likes;
    
    const response = await fetch(`${API_BASE_URL}/recommendations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        preferences: preferences,
        likedProducts: likedProducts
      }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error getting recommendations:', error);
    throw error;
  }
};