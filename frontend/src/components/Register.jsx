import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('student')
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    const res = await fetch('/register', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
      },
      body: new URLSearchParams({ name, email, password, role }),
      redirect: 'follow'
    })

    const data = await res.json().catch(() => null)
    if (res.status < 400) {
      navigate('/login')
      return
    }

    alert('Registration failed: ' + (data?.error || data?.message || res.statusText))
  }

  return (
    <div>
      <h1>Register</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="name">Name:</label>
        <input id="name" type="text" value={name} onChange={e => setName(e.target.value)} required />

        <label htmlFor="email">Email:</label>
        <input id="email" type="email" value={email} onChange={e => setEmail(e.target.value)} required />

        <label htmlFor="password">Password:</label>
        <input id="password" type="password" value={password} onChange={e => setPassword(e.target.value)} required />

        <label htmlFor="role">Role:</label>
        <select id="role" value={role} onChange={e => setRole(e.target.value)}>
          <option value="teacher">Teacher</option>
          <option value="student">Student</option>
        </select>

        <button type="submit">Register</button>
      </form>
    </div>
  )
}
