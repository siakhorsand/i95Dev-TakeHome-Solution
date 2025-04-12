import React from 'react';

const Recommendations = ({ recommendations, isLoading }) => {
  if (isLoading) {
    return (
      <div className="recommendations-container loading">
        <div className="loading-spinner"></div>
        <p>Finding the perfect products for you...</p>
      </div>
    );
  }

  // Message when no recommendations are available
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="recommendations-container empty">
        <p>No recommendations yet. Set your preferences and browse some products!</p>
        <p className="recommendation-tip">Tip: The more products you browse and the more specific your preferences, the better your recommendations will be.</p>
      </div>
    );
  }

  return (
    <div className="recommendations-container">
      <div className="recommendations-list">
        {recommendations.map((recommendation, index) => {
          // Skip recommendations without product data
          if (!recommendation.product) {
            console.warn("Skipping recommendation without product data:", recommendation);
            return null;
          }
          
          try {
            return (
              <div key={recommendation.product.id || index} className="recommendation-card">
                <div className="recommendation-rank">{index + 1}</div>
                
                <div className="recommendation-content">
                  <h3 className="recommendation-name">{recommendation.product.name}</h3>
                  
                  <div className="recommendation-meta">
                    <span className="recommendation-category">{recommendation.product.category}</span>
                    <span className="recommendation-brand">{recommendation.product.brand}</span>
                    <span className="recommendation-price">${recommendation.product.price.toFixed(2)}</span>
                  </div>
                  
                  <div className="recommendation-explanation">
                    <p>{recommendation.explanation}</p>
                  </div>
                  
                  <div className="recommendation-details">
                    <p className="recommendation-description">{recommendation.product.description}</p>
                    {recommendation.product.features && (
                      <div className="recommendation-features">
                        <h4>Key Features:</h4>
                        <ul>
                          {recommendation.product.features.slice(0, 3).map((feature, i) => (
                            <li key={i}>{feature}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          } catch (error) {
            console.error("Error rendering recommendation:", error, recommendation);
            return (
              <div key={index} className="recommendation-card error">
                <p>Error displaying this recommendation.</p>
              </div>
            );
          }
        })}
      </div>
    </div>
  );
};

export default Recommendations;
