import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    // Submit to backend Flask endpoint /login
    const res = await fetch('/login', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
      },
      body: new URLSearchParams({ email, password }),
      redirect: 'follow'
    })

    const data = await res.json().catch(() => null)
    if (res.status < 400) {
      navigate('/dashboard')
      return
    }

    alert('Login failed: ' + (data?.error || data?.message || res.statusText))
  }

  return (
    <div className="login-container">
      <div className="school-logo">
        <img src="/static/images/school_logo.png" alt="School Logo" />
      </div>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" required />
        </div>
        <div className="form-group">
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" required />
        </div>
        <button type="submit">Login</button>
      </form>
    </div>
  )
}
