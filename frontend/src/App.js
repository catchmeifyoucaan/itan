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

const OrishaProfile = ({ orisha, onClose }) => {
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
        <p className="proverb-yoruba">{proverb.proverb.yoruba}</p>
        <p className="proverb-translation">{proverb.proverb.literal_translation}</p>
        <p className="proverb-meaning">{proverb.proverb.meaning}</p>
        <p className="proverb-context"><strong>Usage:</strong> {proverb.proverb.usage_context}</p>
      </div>
    </div>
  );
};

const ProverbShelf = ({ onClose }) => {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [proverbs, setProverbs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/proverbs/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchProverbsByCategory = async (categoryId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/proverbs/category/${categoryId}`);
      setProverbs(response.data.proverbs);
      setSelectedCategory(response.data);
      setSearchResults([]);
    } catch (error) {
      console.error('Error fetching proverbs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/proverbs/search?q=${encodeURIComponent(searchTerm)}`);
      setSearchResults(response.data);
      setSelectedCategory(null);
      setProverbs([]);
    } catch (error) {
      console.error('Error searching proverbs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-container proverb-shelf">
        <div className="modal-header">
          <h2>Òwe Yorùbá (Proverb Shelf)</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="search-section">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search proverbs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <button onClick={handleSearch}>Search</button>
          </div>
        </div>

        <div className="proverb-content">
          {!selectedCategory && searchResults.length === 0 && (
            <div className="categories-grid">
              <h3>Categories</h3>
              <div className="category-cards">
                {categories.map((category) => (
                  <div 
                    key={category.id}
                    className="category-card"
                    onClick={() => fetchProverbsByCategory(category.id)}
                  >
                    <h4>{category.name}</h4>
                    <p>{category.name_yoruba}</p>
                    <span className="proverb-count">{category.count} proverbs</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {selectedCategory && (
            <div className="category-proverbs">
              <div className="category-header">
                <h3>{selectedCategory.name} ({selectedCategory.name_yoruba})</h3>
                <button 
                  className="back-btn"
                  onClick={() => {
                    setSelectedCategory(null);
                    setProverbs([]);
                  }}
                >
                  ← Back to Categories
                </button>
              </div>
              
              {loading ? (
                <div className="loading">Loading proverbs...</div>
              ) : (
                <div className="proverbs-list">
                  {proverbs.map((proverb, index) => (
                    <div key={index} className="proverb-card">
                      <p className="proverb-yoruba">{proverb.yoruba}</p>
                      <p className="proverb-translation">{proverb.literal}</p>
                      <p className="proverb-meaning">{proverb.meaning}</p>
                      <p className="proverb-context"><strong>Usage:</strong> {proverb.context}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {searchResults.length > 0 && (
            <div className="search-results">
              <div className="search-header">
                <h3>Search Results for "{searchTerm}"</h3>
                <button 
                  className="back-btn"
                  onClick={() => {
                    setSearchResults([]);
                    setSearchTerm('');
                  }}
                >
                  ← Clear Search
                </button>
              </div>
              
              <div className="proverbs-list">
                {searchResults.map((result, index) => (
                  <div key={index} className="proverb-card">
                    <div className="category-badge">{result.category_name}</div>
                    <p className="proverb-yoruba">{result.proverb.yoruba}</p>
                    <p className="proverb-translation">{result.proverb.literal}</p>
                    <p className="proverb-meaning">{result.proverb.meaning}</p>
                    <p className="proverb-context"><strong>Usage:</strong> {result.proverb.context}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const FolktaleLibrary = ({ onClose }) => {
  const [folktales, setFolktales] = useState([]);
  const [selectedTale, setSelectedTale] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchFolktales();
  }, []);

  const fetchFolktales = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/folktales`);
      setFolktales(response.data);
    } catch (error) {
      console.error('Error fetching folktales:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectTale = (tale) => {
    setSelectedTale(tale);
  };

  if (selectedTale) {
    return (
      <div className="modal-overlay">
        <div className="modal-container folktale-reader">
          <div className="modal-header">
            <h2>{selectedTale.title}</h2>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
          
          <div className="tale-content">
            <div className="tale-header">
              <h3 className="tale-title-yoruba">{selectedTale.title_yoruba}</h3>
              <p className="tale-summary">{selectedTale.summary}</p>
            </div>
            
            <div className="tale-story">
              <h4>The Story</h4>
              <p className="story-text">{selectedTale.full_story}</p>
            </div>
            
            <div className="tale-moral">
              <h4>Moral of the Story</h4>
              <p className="moral-text">{selectedTale.moral}</p>
            </div>
            
            <div className="tale-characters">
              <h4>Characters</h4>
              <div className="character-list">
                {selectedTale.characters.map((character, index) => (
                  <span key={index} className="character-tag">{character}</span>
                ))}
              </div>
            </div>
            
            <button 
              className="back-btn"
              onClick={() => setSelectedTale(null)}
            >
              ← Back to Tales
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay">
      <div className="modal-container folktale-library">
        <div className="modal-header">
          <h2>Àlọ́ Ìjàpá (Tortoise Tales)</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="library-content">
          <p className="library-intro">
            Welcome to the adventures of Ìjàpá Alápàápàá, the cunning tortoise. 
            These traditional tales teach us about wisdom, consequences, and the 
            complexities of character.
          </p>
          
          {loading ? (
            <div className="loading">Loading tales...</div>
          ) : (
            <div className="tales-grid">
              {folktales.map((tale) => (
                <div 
                  key={tale.id}
                  className="tale-card"
                  onClick={() => selectTale(tale)}
                >
                  <h3>{tale.title}</h3>
                  <p className="tale-title-yoruba">{tale.title_yoruba}</p>
                  <p className="tale-summary">{tale.summary}</p>
                  <div className="tale-characters">
                    {tale.characters.slice(0, 3).map((character, index) => (
                      <span key={index} className="character-tag">{character}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const App = () => {
  const [orishas, setOrishas] = useState([]);
  const [selectedOrisha, setSelectedOrisha] = useState(null);
  const [showProverbShelf, setShowProverbShelf] = useState(false);
  const [showFolktaleLibrary, setShowFolktaleLibrary] = useState(false);
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
        
        <div className="action-buttons">
          <button 
            className="action-btn"
            onClick={() => setShowProverbShelf(true)}
          >
            📚 Òwe Shelf (Proverb Library)
          </button>
          <button 
            className="action-btn"
            onClick={() => setShowFolktaleLibrary(true)}
          >
            🐢 Àlọ́ Ìjàpá (Tortoise Tales)
          </button>
        </div>
      </div>

      <div className="main-content">
        <div className="constellation-container">
          <h2 className="section-title">Òrìṣà Pantheon</h2>
          <p className="section-description">
            Explore the divine constellation of Yorùbá deities. We've expanded the pantheon to include 18 Òrìṣà! 
            Click on any star to learn about their stories, domains, and connections across the diaspora.
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

      {showProverbShelf && (
        <ProverbShelf onClose={() => setShowProverbShelf(false)} />
      )}

      {showFolktaleLibrary && (
        <FolktaleLibrary onClose={() => setShowFolktaleLibrary(false)} />
      )}
    </div>
  );
};

export default App;