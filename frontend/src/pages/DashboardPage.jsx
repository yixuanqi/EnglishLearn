import { useAuth } from '../contexts/AuthContext'
import { Link } from 'react-router-dom'
import './DashboardPage.css'

export default function DashboardPage() {
  const { user } = useAuth()

  const stats = [
    { label: 'Total Sessions', value: '24', trend: '+12%' },
    { label: 'Practice Hours', value: '18.5', trend: '+8%' },
    { label: 'Current Streak', value: '7 days', trend: '+2 days' },
    { label: 'Accuracy Rate', value: '87%', trend: '+5%' }
  ]

  const recentScenarios = [
    { id: 1, title: 'Business Meeting', difficulty: 'Intermediate', progress: 75, lastPracticed: '2 days ago' },
    { id: 2, title: 'Restaurant Ordering', difficulty: 'Beginner', progress: 100, lastPracticed: '5 days ago' },
    { id: 3, title: 'Job Interview', difficulty: 'Advanced', progress: 45, lastPracticed: '1 week ago' }
  ]

  return (
    <div className="dashboard-page">
      <div className="container">
        <div className="dashboard-header">
          <div>
            <h1>🌿 Welcome back, {user?.name?.split(' ')[0]}!</h1>
            <p>Continue your English learning journey in nature</p>
          </div>
          <Link to="/scenarios" className="btn btn-primary">
            🌱 Start Practice
          </Link>
        </div>

        <div className="stats-grid">
          {stats.map((stat, index) => (
            <div key={index} className="stat-card">
              <div className="stat-header">
                <span className="stat-label">{stat.label}</span>
                <span className="stat-trend">{stat.trend}</span>
              </div>
              <div className="stat-value">{stat.value}</div>
            </div>
          ))}
        </div>

        <div className="dashboard-content">
          <div className="recent-section">
            <div className="section-header">
              <h2>Recent Practice</h2>
              <Link to="/scenarios" className="link-gold">View All</Link>
            </div>
            <div className="scenarios-list">
              {recentScenarios.map((scenario) => (
                <div key={scenario.id} className="scenario-card">
                  <div className="scenario-info">
                    <h3>{scenario.title}</h3>
                    <div className="scenario-meta">
                      <span className="badge badge-gold">{scenario.difficulty}</span>
                      <span className="scenario-time">{scenario.lastPracticed}</span>
                    </div>
                  </div>
                  <div className="scenario-progress">
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${scenario.progress}%` }}
                      ></div>
                    </div>
                    <span className="progress-text">{scenario.progress}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="tips-section">
            <div className="section-header">
              <h2>🌿 Learning Tips</h2>
            </div>
            <div className="tips-card">
              <div className="tip-item">
                <div className="tip-icon">🌱</div>
                <div className="tip-content">
                  <h4>Set Daily Goals</h4>
                  <p>Practice for at least 15 minutes every day to build consistency</p>
                </div>
              </div>
              <div className="tip-item">
                <div className="tip-icon">🍃</div>
                <div className="tip-content">
                  <h4>Focus on Pronunciation</h4>
                  <p>Listen carefully and mimic native speakers' intonation</p>
                </div>
              </div>
              <div className="tip-item">
                <div className="tip-icon">🌳</div>
                <div className="tip-content">
                  <h4>Expand Vocabulary</h4>
                  <p>Learn 5 new words daily and use them in conversations</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}