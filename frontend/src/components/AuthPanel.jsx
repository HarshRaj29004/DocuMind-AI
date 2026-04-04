import { useState } from 'react'

function AuthPanel({ onLogin, onRegister, loading, error }) {
  const [mode, setMode] = useState('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [localError, setLocalError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLocalError('')

    if (!email.trim() || !password.trim()) {
      setLocalError('Email and password are required.')
      return
    }

    if (mode === 'login') {
      await onLogin(email, password)
      return
    }

    if (!name.trim()) {
      setLocalError('Name is required for registration.')
      return
    }

    if (password !== confirmPassword) {
      setLocalError('Password and confirm password must match.')
      return
    }

    await onRegister(name, email, password)
  }

  const switchMode = (nextMode) => {
    setMode(nextMode)
    setLocalError('')
  }

  return (
    <section className="auth-shell panel">
      <h2>{mode === 'login' ? 'Login to your workspace' : 'Create your account'}</h2>
      <p className="muted">Each account has isolated document ingestion and retrieval.</p>

      <div className="auth-actions">
        <button
          type="button"
          className={mode === 'login' ? '' : 'secondary'}
          disabled={loading}
          onClick={() => switchMode('login')}
        >
          Login
        </button>
        <button
          type="button"
          className={mode === 'register' ? '' : 'secondary'}
          disabled={loading}
          onClick={() => switchMode('register')}
        >
          Register
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {localError && <div className="error-banner">{localError}</div>}

      <form className="stack" onSubmit={handleSubmit}>
        {mode === 'register' && (
          <>
            <label htmlFor="auth-name">Name</label>
            <input
              id="auth-name"
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Your name"
              disabled={loading}
            />
          </>
        )}

        <label htmlFor="auth-email">Email</label>
        <input
          id="auth-email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
          disabled={loading}
        />

        <label htmlFor="auth-password">Password</label>
        <input
          id="auth-password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Minimum 8 characters"
          disabled={loading}
        />

        {mode === 'register' && (
          <>
            <label htmlFor="auth-confirm-password">Confirm password</label>
            <input
              id="auth-confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              placeholder="Re-enter password"
              disabled={loading}
            />
          </>
        )}

        <div className="auth-actions">
          <button type="submit" disabled={loading}>
            {loading
              ? 'Please wait...'
              : mode === 'login'
                ? 'Login'
                : 'Create account'}
          </button>
        </div>
      </form>
    </section>
  )
}

export default AuthPanel
