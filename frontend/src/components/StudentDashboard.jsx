import React, { useEffect, useState } from 'react'

export default function StudentDashboard() {
  const [attendanceRecords, setAttendanceRecords] = useState([])
  const [classes, setClasses] = useState([])
  const [stats, setStats] = useState({ total:0, present:0, absent:0, rate:0 })

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch('/api/student_dashboard')
        if (!res.ok) return
        const data = await res.json()
        setClasses(data.classes || [])
        setAttendanceRecords(data.attendance_records || [])
        setStats(data.stats || {})
      } catch(e) {}
    }
    load()
  }, [])

  return (
    <div>
      <h1>Student Dashboard</h1>
      <h2>Your Classes</h2>
      <ul>
        {classes.map(c => <li key={c.id}>{c.name}</li>)}
      </ul>

      <h2>Attendance Statistics</h2>
      <p>Total Classes: {stats.total}</p>
      <p>Present: {stats.present}</p>
      <p>Absent: {stats.absent}</p>
      <p>Attendance Rate: {typeof stats.rate === 'number' ? stats.rate.toFixed(2) : stats.rate}%</p>

      <h2>Attendance Records</h2>
      <div className="export-section">
        <a className="btn btn-primary" href={`/export/student_attendance/${/* student id placeholder */ 1}`}>
          Export Attendance History
        </a>
      </div>

      <table>
        <thead>
          <tr><th>Date</th><th>Class</th><th>Status</th></tr>
        </thead>
        <tbody>
          {attendanceRecords.map((r, idx) => (
            <tr key={idx}>
              <td>{r.date}</td>
              <td>{r.class_name}</td>
              <td>{r.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
