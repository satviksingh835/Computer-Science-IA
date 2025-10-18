import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function CreateClass() {
  const [name, setName] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    const res = await fetch('/create_class', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ class_name: name })
    })
    if (res.ok) navigate('/dashboard')
    else alert('Failed')
  }

  return (
    <div>
      <h1>Create New Class</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="class_name">Class Name:</label>
        <input id="class_name" type="text" value={name} onChange={e => setName(e.target.value)} required />
        <button type="submit">Create Class</button>
      </form>
    </div>
  )
}
