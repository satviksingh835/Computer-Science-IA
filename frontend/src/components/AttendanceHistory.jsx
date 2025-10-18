import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

export default function AttendanceHistory() {
  const { classId } = useParams()
  const [studentStats, setStudentStats] = useState([])
  const [sortBy, setSortBy] = useState('name')

  useEffect(() => {
    async function load() {
      const res = await fetch(`/api/attendance_history/${classId}?sort_by=${sortBy}`)
      if (res.ok) setStudentStats(await res.json())
    }
    load()
  }, [classId, sortBy])

  return (
    <div>
      <h2>Attendance History for {classId}</h2>

      <div className="sorting-options">
        <h3>Sort by:</h3>
        <button className={`btn ${sortBy==='name' ? 'active' : ''}`} onClick={() => setSortBy('name')}>Name</button>
        <button className={`btn ${sortBy==='absent' ? 'active' : ''}`} onClick={() => setSortBy('absent')}>Most Absences</button>
        <button className={`btn ${sortBy==='present' ? 'active' : ''}`} onClick={() => setSortBy('present')}>Most Present</button>
        <button className={`btn ${sortBy==='rate' ? 'active' : ''}`} onClick={() => setSortBy('rate')}>Attendance Rate</button>
      </div>

      <div className="attendance-stats">
        {studentStats.map((s, idx) => (
          <div className="student-card" key={idx}>
            <h4>{s.name}</h4>
            <p>Present: {s.present_count}</p>
            <p>Absent: {s.absent_count}</p>
            <p>Attendance Rate: {typeof s.attendance_rate === 'number' ? s.attendance_rate.toFixed(2) : s.attendance_rate}%</p>
            <div className="attendance-details">
              <h5>Attendance Records:</h5>
              <ul>
                {(s.records || []).map((r,i) => (
                  <li key={i}>{r.date} - <span className={r.status==='present' ? 'text-success' : 'text-danger'}>{r.status}</span></li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
