import React, { useEffect, useState } from 'react';

const UserPreferences = ({ preferences, products, onPreferencesChange }) => {
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);

  useEffect(() => {
    if (products && products.length) {
      const uniqueCategories = [...new Set(products.map(product => product.category))];
      setCategories(uniqueCategories);

      const uniqueBrands = [...new Set(products.map(product => product.brand))];
      setBrands(uniqueBrands);
    }
  }, [products]);

  // Handle price range changes
  const handlePriceRangeChange = (e) => {
    onPreferencesChange({ priceRange: e.target.value });
  };

  // Handle category selection
  const handleCategoryChange = (category) => {
    const updatedCategories = [...preferences.categories];
    
    if (updatedCategories.includes(category)) {
      // Remove category if already selected
      const index = updatedCategories.indexOf(category);
      updatedCategories.splice(index, 1);
    } else {
      // Add category if not selected
      updatedCategories.push(category);
    }
    
    onPreferencesChange({ categories: updatedCategories });
  };

  // Handle brand selection
  const handleBrandChange = (brand) => {
    const updatedBrands = [...preferences.brands];
    
    if (updatedBrands.includes(brand)) {
      // Remove brand if already selected
      const index = updatedBrands.indexOf(brand);
      updatedBrands.splice(index, 1);
    } else {
      // Add brand if not selected
      updatedBrands.push(brand);
    }
    
    onPreferencesChange({ brands: updatedBrands });
  };

  return (
    <div className="preferences-container">
      <h3>Your Preferences</h3>
      
      {/* Price Range Selection */}
      <div className="preference-section">
        <h4>Price Range</h4>
        <select 
          value={preferences.priceRange} 
          onChange={handlePriceRangeChange}
          className="price-select"
        >
          <option value="all">All Prices</option>
          <option value="0-50">Under $50</option>
          <option value="50-100">$50 - $100</option>
          <option value="100+">Over $100</option>
        </select>
      </div>
      
      {/* Categories Selection */}
      <div className="preference-section">
        <h4>Categories</h4>
        <div className="category-buttons">
          {categories.map(category => (
            <button
              key={category}
              className={`category-button ${preferences.categories.includes(category) ? 'active' : ''}`}
              onClick={() => handleCategoryChange(category)}
            >
              {category}
            </button>
          ))}
        </div>
      </div>
      
      {/* Brands Selection */}
      <div className="preference-section">
        <h4>Brands</h4>
        <div className="checkbox-group">
          {brands.map(brand => (
            <label key={brand} className="checkbox-label">
              <input
                type="checkbox"
                checked={preferences.brands.includes(brand)}
                onChange={() => handleBrandChange(brand)}
              />
              {brand}
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};

export default UserPreferences;