import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  // This component mirrors `dashboard.html` for teachers; for simplicity
  // it fetches a `/api/classes` endpoint which you can implement in Flask.
  const [classes, setClasses] = useState([])

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch('/api/classes')
        if (res.ok) setClasses(await res.json())
      } catch (e) {
        // fallback: leave empty or mock data
      }
    }
    load()
  }, [])

  return (
    <div>
      <h1>Dashboard</h1>
      <h2>Your Classes</h2>
      <div className="class-selector">
        <select id="classSelect" onChange={e => {
          const id = e.target.value
          document.querySelectorAll('.class-details').forEach(div => div.style.display = 'none')
          if (id) document.getElementById('class-' + id).style.display = 'block'
        }}>
          <option value="">Select a class</option>
          {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>

      {classes.map(c => (
        <div id={`class-${c.id}`} className="class-details" style={{ display: 'none' }} key={c.id}>
          <h3>{c.name}</h3>
          <Link to={`/mark-attendance/${c.id}`} className="btn">Mark Attendance</Link>
          <Link to={`/attendance-history/${c.id}`} className="btn btn-info">View Attendance History</Link>
          <a className="btn btn-primary" href={`/export/class_attendance/${c.id}`}>Export Class Attendance</a>

          <form className="add-student-form" onSubmit={async (e) => {
            e.preventDefault();
            const form = e.target
            const email = form.student_email.value
            const res = await fetch(`/add_student/${c.id}`, {
              method: 'POST',
              credentials: 'include',
              headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
              body: new URLSearchParams({ student_email: email })
            })
            if (res.ok) alert('Student added')
            else alert('Failed to add student')
          }}>
            <input name="student_email" placeholder="Student Email" required />
            <button type="submit">Add Student</button>
          </form>

          <h4>Students:</h4>
          <ul className="student-list">
            {(c.students || []).map(s => (
              <li key={s.id}>
                {s.name}
                <form method="POST" action={`/remove_student/${c.id}/${s.id}`} style={{ display: 'inline' }}>
                  <button type="submit" className="btn btn-danger">Remove</button>
                </form>
              </li>
            ))}
          </ul>
        </div>
      ))}

      <Link to="/create-class" className="btn create-class">Create New Class</Link>
    </div>
  )
}
