import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ScenariosPage from './pages/ScenariosPage'
import PracticePage from './pages/PracticePage'
import DashboardPage from './pages/DashboardPage'

function App() {
  return (
    <AuthProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/scenarios" element={<ScenariosPage />} />
          <Route path="/practice/:scenarioId" element={<PracticePage />} />
        </Routes>
      </Layout>
    </AuthProvider>
  )
}

export default App