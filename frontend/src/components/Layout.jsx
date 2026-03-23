import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Layout.css'

export default function Layout({ children }) {
  const { user, isAuthenticated, logout } = useAuth()
  const location = useLocation()

  const isAuthPage = ['/login', '/register'].includes(location.pathname)

  if (isAuthPage) {
    return <div className="auth-layout">{children}</div>
  }

  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="container header-content">
          <Link to="/dashboard" className="logo">
            <span className="logo-icon">🌿</span>
            <span className="logo-text">Forest English</span>
          </Link>
          
          <nav className="nav-menu">
            <Link to="/dashboard" className={`nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}>
              🌱 Home
            </Link>
            <Link to="/scenarios" className={`nav-link ${location.pathname === '/scenarios' ? 'active' : ''}`}>
              🌲 Scenarios
            </Link>
          </nav>

          <div className="user-menu">
            {isAuthenticated ? (
              <>
                <div className="user-info">
                  <span className="user-name">{user?.name}</span>
                  <span className="user-level">{user?.english_level || 'Beginner'}</span>
                </div>
                <button onClick={logout} className="btn-logout">
                  Sign Out
                </button>
              </>
            ) : (
              <Link to="/login" className="btn btn-primary">
                Sign In
              </Link>
            )}
          </div>
        </div>
      </header>

      <main className="app-main">
        {children}
      </main>

      <footer className="app-footer">
        <div className="container footer-content">
          <p>© 2024 English Trainer. AI-Powered Language Learning.</p>
          <div className="footer-links">
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Support</a>
          </div>
        </div>
      </footer>
    </div>
  )
}