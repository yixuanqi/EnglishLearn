import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import './ScenariosPage.css'

const API_BASE = 'http://localhost:8000/api/v1'

export default function ScenariosPage() {
  const [scenarios, setScenarios] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetchScenarios()
  }, [filter, search])

  const fetchScenarios = async () => {
    try {
      setLoading(true)
      const params = {}
      if (filter !== 'all') params.difficulty = filter
      if (search) params.search = search

      const response = await axios.get(`${API_BASE}/scenarios`, { params })
      setScenarios(response.data.items || [])
    } catch (error) {
      console.error('Failed to fetch scenarios:', error)
    } finally {
      setLoading(false)
    }
  }

  const difficulties = ['all', 'beginner', 'intermediate', 'advanced']

  return (
    <div className="scenarios-page">
      <div className="container">
        <div className="page-header">
          <div>
            <h1>🌿 Practice Scenarios</h1>
            <p>Choose your learning path in the forest</p>
          </div>
        </div>

        <div className="filters-bar">
          <div className="search-box">
            <input
              type="text"
              className="input"
              placeholder="🔍 Search scenarios..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="filter-buttons">
            {difficulties.map((diff) => (
              <button
                key={diff}
                className={`filter-btn ${filter === diff ? 'active' : ''}`}
                onClick={() => setFilter(diff)}
              >
                {diff.charAt(0).toUpperCase() + diff.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading scenarios...</p>
          </div>
        ) : scenarios.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🌲</div>
            <h3>No scenarios found</h3>
            <p>Try adjusting your filters or search terms</p>
          </div>
        ) : (
          <div className="scenarios-grid">
            {scenarios.map((scenario, index) => (
              <Link
                key={scenario.id}
                to={`/practice/${scenario.id}`}
                className="scenario-card"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="scenario-image">
                  <div className="scenario-overlay">
                    <div className="play-icon">▶</div>
                  </div>
                  {scenario.is_premium && (
                    <div className="premium-badge">
                      <span>✦</span> Premium
                    </div>
                  )}
                </div>
                <div className="scenario-content">
                  <div className="scenario-header">
                    <h3>{scenario.title}</h3>
                    <span className={`difficulty-badge ${scenario.difficulty}`}>
                      {scenario.difficulty}
                    </span>
                  </div>
                  <p className="scenario-description">{scenario.description}</p>
                  <div className="scenario-footer">
                    <div className="scenario-meta">
                      <span className="meta-item">
                        <span className="meta-icon">⏱</span>
                        {scenario.estimated_duration} min
                      </span>
                      <span className="meta-item">
                        <span className="meta-icon">📂</span>
                        {scenario.category}
                      </span>
                    </div>
                    <div className="start-btn">Start Practice</div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}