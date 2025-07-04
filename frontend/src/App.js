import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const OrishaConstellation = ({ orisha, onOrishaClick, selectedOrisha }) => {
  const isSelected = selectedOrisha === orisha.id;
  
  return (
    <div
      className={`orisha-star ${isSelected ? 'selected' : ''}`}
      style={{
        left: `${orisha.constellation_position.x}%`,
        top: `${orisha.constellation_position.y}%`,
      }}
      onClick={() => onOrishaClick(orisha)}
    >
      <div className="star-glow"></div>
      <div className="star-core"></div>
      <div className="orisha-name">{orisha.name}</div>
    </div>
  );
};

const OrishaProfile = ({ orisha, onClose, onTranslate }) => {
  const [language, setLanguage] = useState('english');
  const [translatedContent, setTranslatedContent] = useState({});
  const [loading, setLoading] = useState(false);

  const handleTranslate = async () => {
    if (language === 'yoruba' && !translatedContent.story) {
      setLoading(true);
      try {
        const response = await axios.post(`${API}/translate`, {
          text: orisha.story,
          target_language: 'yoruba'
        });
        setTranslatedContent(prev => ({
          ...prev,
          story: response.data.translated_text
        }));
      } catch (error) {
        console.error('Translation error:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    if (language === 'yoruba') {
      handleTranslate();
    }
  }, [language, orisha]);

  const currentStory = language === 'yoruba' 
    ? (translatedContent.story || orisha.yoruba_story)
    : orisha.story;

  return (
    <div className="orisha-profile-overlay">
      <div className="orisha-profile-container">
        <div className="profile-header">
          <button className="close-btn" onClick={onClose}>×</button>
          <div className="language-toggle">
            <button 
              className={language === 'english' ? 'active' : ''}
              onClick={() => setLanguage('english')}
            >
              English
            </button>
            <button 
              className={language === 'yoruba' ? 'active' : ''}
              onClick={() => setLanguage('yoruba')}
            >
              Yorùbá
            </button>
          </div>
        </div>
        
        <div className="profile-content">
          <h1 className="orisha-title">{orisha.name}</h1>
          <div className="orisha-subtitle">{orisha.yoruba_name}</div>
          
          <div className="orisha-attributes">
            <div className="attribute-group">
              <h3>Domains</h3>
              <div className="attribute-tags">
                {orisha.domains.map((domain, index) => (
                  <span key={index} className="attribute-tag">{domain}</span>
                ))}
              </div>
            </div>
            
            <div className="attribute-group">
              <h3>Sacred Colors</h3>
              <div className="color-palette">
                {orisha.colors.map((color, index) => (
                  <div 
                    key={index} 
                    className="color-swatch"
                    style={{ backgroundColor: color.toLowerCase() }}
                  ></div>
                ))}
              </div>
            </div>
            
            <div className="attribute-group">
              <h3>Sacred Number</h3>
              <div className="sacred-number">{orisha.sacred_number}</div>
            </div>
          </div>
          
          <div className="story-section">
            <h3>Story</h3>
            {loading ? (
              <div className="loading">Translating...</div>
            ) : (
              <p className="story-text">{currentStory}</p>
            )}
          </div>
          
          <div className="diaspora-section">
            <h3>Diaspora Connections</h3>
            <div className="diaspora-info">
              <div className="diaspora-item">
                <strong>Santería:</strong> {orisha.diaspora.santeria}
              </div>
              <div className="diaspora-item">
                <strong>Regions:</strong> {orisha.diaspora.location}
              </div>
            </div>
          </div>
          
          <div className="symbols-section">
            <h3>Sacred Symbols</h3>
            <div className="symbols-list">
              {orisha.symbols.map((symbol, index) => (
                <span key={index} className="symbol-item">{symbol}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const DailyProverb = () => {
  const [proverb, setProverb] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDailyProverb = async () => {
      try {
        const response = await axios.get(`${API}/proverbs/daily`);
        setProverb(response.data);
      } catch (error) {
        console.error('Error fetching daily proverb:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDailyProverb();
  }, []);

  if (loading) return <div className="loading">Loading proverb...</div>;
  if (!proverb) return null;

  return (
    <div className="daily-proverb">
      <h3>Òwe Oni (Today's Proverb)</h3>
      <div className="proverb-content">
        {typeof proverb.proverb === 'string' ? (
          <p>{proverb.proverb}</p>
        ) : (
          <div>
            <p className="proverb-yoruba">{proverb.proverb.yoruba}</p>
            <p className="proverb-translation">{proverb.proverb.literal_translation}</p>
            <p className="proverb-meaning">{proverb.proverb.meaning}</p>
          </div>
        )}
      </div>
    </div>
  );
};

const App = () => {
  const [orishas, setOrishas] = useState([]);
  const [selectedOrisha, setSelectedOrisha] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrishas = async () => {
      try {
        const response = await axios.get(`${API}/orisha`);
        setOrishas(response.data);
      } catch (error) {
        console.error('Error fetching Òrìṣà:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOrishas();
  }, []);

  const handleOrishaClick = (orisha) => {
    setSelectedOrisha(orisha);
  };

  const handleCloseProfile = () => {
    setSelectedOrisha(null);
  };

  return (
    <div className="app">
      <div className="app-header">
        <h1 className="app-title">The Living Ìtàn</h1>
        <p className="app-subtitle">Àkọsílẹ̀ Àṣà Yorùbá Digital Encyclopedia</p>
      </div>

      <div className="cultural-pulse">
        <DailyProverb />
      </div>

      <div className="main-content">
        <div className="constellation-container">
          <h2 className="section-title">Òrìṣà Pantheon</h2>
          <p className="section-description">
            Explore the divine constellation of Yorùbá deities. Click on any star to learn about their stories, domains, and connections across the diaspora.
          </p>
          
          {loading ? (
            <div className="loading">Loading constellation...</div>
          ) : (
            <div className="constellation-map">
              {orishas.map((orisha) => (
                <OrishaConstellation
                  key={orisha.id}
                  orisha={orisha}
                  onOrishaClick={handleOrishaClick}
                  selectedOrisha={selectedOrisha?.id}
                />
              ))}
              <div className="constellation-lines"></div>
            </div>
          )}
        </div>
      </div>

      {selectedOrisha && (
        <OrishaProfile
          orisha={selectedOrisha}
          onClose={handleCloseProfile}
        />
      )}
    </div>
  );
};

export default App;