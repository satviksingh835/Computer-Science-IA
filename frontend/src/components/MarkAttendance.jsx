import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

export default function MarkAttendance() {
  const { classId } = useParams()
  const [students, setStudents] = useState([])
  const [date, setDate] = useState('')
  const navigate = useNavigate()

  // In a full implementation you'd fetch student list for classId
  React.useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`/api/class/${classId}`, { credentials: 'include' })
        // If backend redirected to login or returned 401/403, navigate to login
        if (res.status === 401 || res.status === 403 || res.redirected) {
          alert('You must be logged in to mark attendance')
          window.location.href = '/login'
          return
        }
        if (!res.ok) return
        const data = await res.json()
        // initialize student statuses
        const withStatus = (data.students || []).map(s => ({ ...s, status: 'present' }))
        setStudents(withStatus)
      } catch (e) {
        console.error(e)
      }
    }
    load()
  }, [classId])

  async function handleSubmit(e) {
    e.preventDefault()
    // Build JSON payload
    const records = students.map(s => ({ student_id: s.id, status: s.status }))
    const res = await fetch(`/api/mark_attendance/${classId}`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ date, records })
    })
    const data = await res.json().catch(() => null)
    if (res.status === 401 || res.status === 403 || res.redirected) {
      alert('You must be logged in to submit attendance')
      window.location.href = '/login'
      return
    }

    if (res.ok) {
      navigate('/dashboard')
    } else {
      alert('Failed to save attendance: ' + (data?.error || data?.message || res.statusText))
    }
  }

  return (
    <div>
      <h1>Mark Attendance for {classId}</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="date">Date:</label>
        <input id="date" type="date" value={date} onChange={e => setDate(e.target.value)} required />

        <table>
          <thead>
            <tr><th>Student</th><th>Status</th></tr>
          </thead>
          <tbody>
            {students.map(s => (
              <tr key={s.id}>
                <td>{s.email}</td>
                <td>
                  <select value={s.status} onChange={e => setStudents(prev => prev.map(p => p.id === s.id ? { ...p, status: e.target.value } : p))} required>
                    <option value="present">Present</option>
                    <option value="absent">Absent</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <button type="submit">Submit Attendance</button>
      </form>
    </div>
  )
}
