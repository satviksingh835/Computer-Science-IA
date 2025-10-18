import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './components/Home'
import Login from './components/Login'
import Register from './components/Register'
import Dashboard from './components/Dashboard'
import StudentDashboard from './components/StudentDashboard'
import CreateClass from './components/CreateClass'
import MarkAttendance from './components/MarkAttendance'
import AttendanceHistory from './components/AttendanceHistory'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/student" element={<StudentDashboard />} />
        <Route path="/create-class" element={<CreateClass />} />
        <Route path="/mark-attendance/:classId" element={<MarkAttendance />} />
        <Route path="/attendance-history/:classId" element={<AttendanceHistory />} />
      </Routes>
    </Layout>
  )
}
