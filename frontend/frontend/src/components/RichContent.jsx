import './RichContent.css';

function RichContent({ data }) {
  const { type, data: contentData } = data;

  if (type === 'disease-card') {
    return (
      <div className="rich-content disease-card">
        <h4 className="card-title">🦠 Detected Diseases</h4>
        {contentData.map((disease, idx) => (
          <div key={idx} className="disease-item">
            <div className="disease-header">
              <span className="disease-name">{disease.name}</span>
              <span className={`severity-badge ${disease.severity.toLowerCase()}`}>
                {disease.severity}
              </span>
            </div>
            <p className="disease-treatment">💊 {disease.treatment}</p>
          </div>
        ))}
        <button className="action-btn">Learn More</button>
      </div>
    );
  }

  if (type === 'soil-card') {
    return (
      <div className="rich-content soil-card">
        <h4 className="card-title">🌱 Soil Health Report</h4>
        <div className="soil-metrics">
          <div className="metric">
            <span className="metric-label">pH Level</span>
            <span className="metric-value">{contentData.pH}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Nitrogen</span>
            <span className="metric-value">{contentData.nitrogen}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Phosphorus</span>
            <span className="metric-value">{contentData.phosphorus}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Potassium</span>
            <span className="metric-value">{contentData.potassium}</span>
          </div>
        </div>
        <div className="recommendation-box">
          <strong>📋 Recommendation:</strong>
          <p>{contentData.recommendation}</p>
        </div>
      </div>
    );
  }

  if (type === 'weather-card') {
    return (
      <div className="rich-content weather-card">
        <h4 className="card-title">🌤️ Agricultural Weather</h4>
        <div className="weather-grid">
          <div className="weather-item">
            <span className="weather-icon">🌡️</span>
            <span className="weather-label">Temperature</span>
            <span className="weather-value">{contentData.temperature}</span>
          </div>
          <div className="weather-item">
            <span className="weather-icon">💧</span>
            <span className="weather-label">Humidity</span>
            <span className="weather-value">{contentData.humidity}</span>
          </div>
          <div className="weather-item">
            <span className="weather-icon">🌧️</span>
            <span className="weather-label">Rainfall</span>
            <span className="weather-value">{contentData.rainfall}</span>
          </div>
        </div>
        <div className="recommendation-box">
          <strong>💡 Action:</strong>
          <p>{contentData.recommendation}</p>
        </div>
      </div>
    );
  }

  if (type === 'fertilizer-card') {
    return (
      <div className="rich-content fertilizer-card">
        <h4 className="card-title">🧪 Fertilizer Recommendation</h4>
        <div className="fertilizer-details">
          <div className="detail-row">
            <span className="detail-label">NPK Ratio:</span>
            <span className="detail-value">{contentData.npk}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Amount:</span>
            <span className="detail-value">{contentData.amount}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Timing:</span>
            <span className="detail-value">{contentData.timing}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Est. Cost:</span>
            <span className="detail-value cost">{contentData.cost}</span>
          </div>
        </div>
        <button className="action-btn primary">Add to Calendar</button>
      </div>
    );
  }

  return null;
}

export default RichContent;
