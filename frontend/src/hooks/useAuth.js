import { useEffect, useState } from 'react'
import { getMe, loginUser, registerUser, clearToken, getStoredUser } from '../services/api'

export function useAuth() {
  const [user, setUser] = useState(getStoredUser())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const init = async () => {
      if (!user) {
        return
      }
      try {
        await getMe()
      } catch {
        clearToken()
        setUser(null)
      }
    }

    init()
  }, [user])

  const login = async (email, password) => {
    setLoading(true)
    setError(null)
    try {
      const result = await loginUser(email, password)
      setUser(result.user)
      return result.user
    } catch (err) {
      setError(err.message || 'Login failed')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const register = async (name, email, password) => {
    setLoading(true)
    setError(null)
    try {
      const result = await registerUser(name, email, password)
      setUser(result.user)
      return result.user
    } catch (err) {
      setError(err.message || 'Registration failed')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    clearToken()
    setUser(null)
    setError(null)
  }

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
  }
}
