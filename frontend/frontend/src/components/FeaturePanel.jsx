import './FeaturePanel.css';

function FeaturePanel({ onFeatureSelect }) {
  const features = [
    {
      icon: '🦠',
      title: 'Crop Disease Detector',
      description: 'Identify and treat plant diseases',
      query: 'Help me identify crop diseases'
    },
    {
      icon: '🌱',
      title: 'Soil Health Advisor',
      description: 'Analyze soil quality and nutrients',
      query: 'Check my soil health'
    },
    {
      icon: '🌤️',
      title: 'Weather Alerts',
      description: 'Agricultural weather forecasts',
      query: 'Show me weather forecast'
    },
    {
      icon: '🌲',
      title: 'Forestry Management',
      description: 'Forest health and conservation',
      query: 'Forestry management guidance'
    },
    {
      icon: '🧪',
      title: 'Fertilizer Guide',
      description: 'Smart fertilizer recommendations',
      query: 'Recommend fertilizers for my crop'
    },
    {
      icon: '📅',
      title: 'Planting Calendar',
      description: 'Optimal planting & harvest times',
      query: 'Show planting calendar'
    }
  ];

  return (
    <div className="feature-panel">
      <h3 className="panel-title">🌿 How can I assist you today?</h3>
      <div className="features-grid">
        {features.map((feature, idx) => (
          <button
            key={idx}
            className="feature-card"
            onClick={() => onFeatureSelect(feature.query)}
          >
            <div className="feature-icon">{feature.icon}</div>
            <h4 className="feature-title">{feature.title}</h4>
            <p className="feature-description">{feature.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}

export default FeaturePanel;
