import React from 'react';

const LikedProducts = ({ history, products, onClearHistory }) => {
  const likedProducts = products
    .filter(product => history.includes(product.id))
    .map(product => ({
      id: product.id,
      name: product.name,
      price: product.price,
      category: product.category
    }));

  // If no liked products show  empty state
  if (likedProducts.length === 0) {
    return (
      <div className="history-container">
        <h3>Liked Products</h3>
        <p className="empty-history">No products liked yet. Click the heart icon on products in the catalog to like them.</p>
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="history-header">
        <h3>Liked Products ({likedProducts.length})</h3>
        <button 
          onClick={onClearHistory}
          className="clear-history-btn"
        >
          Clear All
        </button>
      </div>
      
      <div className="history-items">
        {likedProducts.map(product => (
          <div key={product.id} className="history-item">
            <div className="history-item-name">{product.name}</div>
            <div className="history-item-meta">
              <span className="history-item-category">{product.category}</span>
              <span className="history-item-price">${product.price.toFixed(2)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LikedProducts;