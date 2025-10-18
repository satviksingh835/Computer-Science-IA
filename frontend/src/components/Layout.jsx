import React from 'react'
import { Link } from 'react-router-dom'

export default function Layout({ children }) {
  // This Layout replaces `base.html`. You can expand the auth logic to
  // read a real user object from an API or context.
  const currentUser = null // placeholder; replace with real auth state

  return (
    <div>
      <header>
        <nav>
          <ul>
            <li><Link to="/">Home</Link></li>
            {!currentUser && (
              <>
                <li><Link to="/login">Login</Link></li>
                <li><Link to="/register">Register</Link></li>
              </>
            )}
            {currentUser && currentUser.role === 'teacher' && (
              <li><Link to="/dashboard">Dashboard</Link></li>
            )}
            {currentUser && currentUser.role === 'student' && (
              <li><Link to="/student">Student Dashboard</Link></li>
            )}
            {currentUser && (
              <li><a href="#" onClick={() => {/* call logout endpoint */}}>Logout</a></li>
            )}
          </ul>
        </nav>
      </header>

      <main>
        {children}
      </main>
    </div>
  )
}
