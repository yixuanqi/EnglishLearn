import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext(null)

const API_BASE = 'http://localhost:8000/api/v1'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('token')
      setToken(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    const response = await axios.post(`${API_BASE}/auth/login`, {
      email,
      password
    })
    const { access_token, user: userData } = response.data
    localStorage.setItem('token', access_token)
    setToken(access_token)
    setUser(userData)
    return userData
  }

  const register = async (name, email, password) => {
    const response = await axios.post(`${API_BASE}/auth/register`, {
      name,
      email,
      password
    })
    const { access_token, user: userData } = response.data
    localStorage.setItem('token', access_token)
    setToken(access_token)
    setUser(userData)
    return userData
  }

  const logout = async () => {
    try {
      await axios.post(`${API_BASE}/auth/logout`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('token')
      setToken(null)
      setUser(null)
    }
  }

  const updateProfile = async (data) => {
    const response = await axios.patch(`${API_BASE}/auth/me`, data, {
      headers: { Authorization: `Bearer ${token}` }
    })
    setUser(response.data)
    return response.data
  }

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      login,
      register,
      logout,
      updateProfile,
      isAuthenticated: !!user
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}