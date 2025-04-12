import React from 'react';

const Catalog = ({ products, onProductClick, likedProducts }) => {
  // If no products, show a loading message
  if (!products || products.length === 0) {
    return (
      <div className="catalog-container">
        <p className="empty-catalog">No products match your current filter criteria. Try adjusting your filters.</p>
      </div>
    );
  }

  const isLiked = (productId) => {
    return likedProducts.includes(productId);
  };

  return (
    <div className="catalog-container">
      <div className="catalog-instructions">
        <p>Click the heart icon to like a product. Click again to unlike it.</p>
      </div>
      <div className="product-grid">
        {products.map((product) => (
          <div 
            key={product.id} 
            className={`product-card ${isLiked(product.id) ? 'product-liked' : ''}`}
          >
            {/* Heart icon for liking products */}
            <div 
              className={`like-button ${isLiked(product.id) ? 'liked' : ''}`}
              onClick={() => onProductClick(product.id)}
              title={isLiked(product.id) ? "Unlike this product" : "Like this product"}
            >
              ♥
            </div>
            
            <div className="product-info">
              <h3 className="product-name">{product.name}</h3>
              <div className="product-meta">
                <span className="product-category">{product.category}</span>
                <span className="product-brand">{product.brand}</span>
              </div>
              <div className="product-price">${product.price.toFixed(2)}</div>
              {product.rating && (
                <div className="product-rating">
                  Rating: {product.rating} ★
                </div>
              )}
              <p className="product-description">{product.description.substring(0, 100)}...</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Catalog;