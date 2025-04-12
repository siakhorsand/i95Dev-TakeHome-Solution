import React, { useState, useEffect } from 'react';
import './styles/App.css';
import Catalog from './components/Catalog';
import LikedProducts from './components/BrowsingHistory';
import Recommendations from './components/Recommendations';
import UserPreferences from './components/UserPreferences';
import { fetchProducts, getRecommendations } from './services/api';
// State variables
function App() {

  const [products, setProducts] = useState([]);
  
  const [likedProducts, setLikedProducts] = useState([]);
  
  const [recommendations, setRecommendations] = useState([]);
  
  const [isLoading, setIsLoading] = useState(false);
  
  const [notification, setNotification] = useState(null);
  
  const [sortCriteria, setSortCriteria] = useState({
    type: 'none',
    order: 'asc'
  });
  
  const [showRecommendationsModal, setShowRecommendationsModal] = useState(false);
  
  const [userPreferences, setUserPreferences] = useState({
    priceRange: 'all',
    categories: [],
    brands: []
  });
  
  useEffect(() => {
    const loadProducts = async () => {
      try {
        const data = await fetchProducts();
        setProducts(data);
      } catch (error) {
        console.error('Error fetching products:', error);
        showNotification('Failed to load products. Please refresh the page.');
      }
    };
    
    loadProducts();
  }, []);
  
  // Filter products based on user preferences
  const filteredProducts = React.useMemo(() => {
    if (!products || products.length === 0) return [];
    
    return products.filter(product => {
      // Filter by price range
      if (userPreferences.priceRange !== 'all') {
        const [min, max] = userPreferences.priceRange.split('-').map(Number);
        if (product.price < min || (max && product.price > max)) {
          return false;
        }
      }
      
      // Filter by categories
      if (userPreferences.categories.length > 0 && 
          !userPreferences.categories.includes(product.category)) {
        return false;
      }
      
      // Filter by brands
      if (userPreferences.brands.length > 0 && 
          !userPreferences.brands.includes(product.brand)) {
        return false;
      }
      
      return true;
    });
  }, [products, userPreferences]);
  
  // Show notification message with automatic disappearing
  const showNotification = (message, isError = true) => {
    setNotification({
      message,
      isError
    });
    
    // Clear notification after 5 seconds
    setTimeout(() => {
      setNotification(null);
    }, 5000);
  };
  
  // Handle product click to toggle in liked products
  const handleProductLike = (productId) => {
    if (likedProducts.includes(productId)) {
      // If product is already liked, unlike it
      setLikedProducts(likedProducts.filter(id => id !== productId));
    } else {
      // If product is not liked, like it
      setLikedProducts([...likedProducts, productId]);
    }
  };
  
  // Handle sorting change
  const handleSortChange = (type, order = 'asc') => {
    setSortCriteria({
      type,
      order
    });
  };
  
  // Handle preference changes
  const handlePreferenceChange = (changes) => {
    setUserPreferences({
      ...userPreferences,
      ...changes
    });
  };
  
  // Get recommendations based on preferences and liked products
  const handleGetRecommendations = async () => {
    // Check if liked products list is empty
    if (likedProducts.length === 0) {
      showNotification('Please like at least one product from the catalog first.');
      return;
    }
    
    setIsLoading(true);
    
    try {
      // Format liked products to include necessary product details
      const likedProductsObjects = likedProducts.map(id => {
        const product = products.find(p => p.id === id);
        return {
          id: product.id,
          name: product.name,
          category: product.category,
          brand: product.brand,
          price: product.price
        };
      });
      
      const data = await getRecommendations(userPreferences, likedProductsObjects);
      
      // Check if we have valid data
      if (!data || typeof data !== 'object') {
        console.error("Invalid response format - not an object:", data);
        showNotification('Received invalid response from server.');
        return;
      }
      
      // Ensure we have recommendations array
      if (!data.recommendations || !Array.isArray(data.recommendations)) {
        console.error("Invalid recommendations format:", data.recommendations);
        showNotification('Received invalid recommendation data structure.');
        return;
      }
      
      setRecommendations(data.recommendations);
      
      // Show success message if recommendations were found
      if (data.recommendations.length > 0) {
        showNotification('Recommendations generated successfully!', false);
      } else {
        showNotification('No recommendations found. Try liking different products or changing your preferences.');
      }
    } catch (error) {
      console.error('Error getting recommendations:', error);
      showNotification('Failed to get recommendations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Clear liked products
  const handleClearLikes = () => {
    setLikedProducts([]);
  };
  
  // Toggle recommendations modal
  const toggleRecommendationsModal = () => {
    setShowRecommendationsModal(!showRecommendationsModal);
  };
  
  return (
    <div className="app">
      <header className="app-header">
        <h1>AI-Powered Product Recommendation Engine</h1>
      </header>
      
      {notification && (
        <div className={`notification ${notification.isError ? 'error' : 'success'}`}>
          {notification.message}
        </div>
      )}
      
      {showRecommendationsModal && (
        <div className="modal-overlay" onClick={toggleRecommendationsModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={toggleRecommendationsModal}>×</button>
            <h2>Your Personalized Recommendations</h2>
            <Recommendations 
              recommendations={recommendations}
              isLoading={false}
            />
          </div>
        </div>
      )}
      
      <main className="app-content">
        <div className="user-section">
          <div className="sort-options">
            <h3>Sort & Filter Options</h3>
            
            <UserPreferences
              preferences={userPreferences}
              products={products}
              onPreferencesChange={handlePreferenceChange}
            />
            
            <div className="sort-section">
              <h4>Sort by:</h4>
              <div className="sort-buttons">
                <button 
                  className={`sort-button ${sortCriteria.type === 'price' && sortCriteria.order === 'asc' ? 'active' : ''}`}
                  onClick={() => handleSortChange('price', 'asc')}
                >
                  Price: Low to High
                </button>
                <button 
                  className={`sort-button ${sortCriteria.type === 'price' && sortCriteria.order === 'desc' ? 'active' : ''}`}
                  onClick={() => handleSortChange('price', 'desc')}
                >
                  Price: High to Low
                </button>
                <button 
                  className={`sort-button ${sortCriteria.type === 'rating' && sortCriteria.order === 'desc' ? 'active' : ''}`}
                  onClick={() => handleSortChange('rating', 'desc')}
                >
                  Highest Rating
                </button>
                <button 
                  className={`sort-button ${sortCriteria.type === 'category' && sortCriteria.order === 'asc' ? 'active' : ''}`}
                  onClick={() => handleSortChange('category', 'asc')}
                >
                  Category (A-Z)
                </button>
                <button 
                  className={`sort-button ${sortCriteria.type === 'none' ? 'active' : ''}`}
                  onClick={() => handleSortChange('none')}
                >
                  Clear Sorting
                </button>
              </div>
            </div>
          </div>
          
          <LikedProducts 
            history={likedProducts}
            products={products}
            onClearHistory={handleClearLikes}
          />
          
          <button 
            className="get-recommendations-btn"
            onClick={handleGetRecommendations}
            disabled={isLoading}
          >
            {isLoading ? 'Getting Recommendations...' : 'Get Personalized Recommendations'}
          </button>
          
          {recommendations.length > 0 && (
            <button 
              className="see-recommendations-btn"
              onClick={toggleRecommendationsModal}
            >
              See Recommendations
            </button>
          )}
        </div>
        
        <div className="catalog-section">
          <h2>Product Catalog</h2>
          
          <Catalog 
            products={filteredProducts}
            onProductClick={handleProductLike}
            likedProducts={likedProducts}
          />
        </div>
      </main>
    </div>
  );
}

export default App;