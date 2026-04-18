import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-6">
              <span className="font-semibold text-gray-900 cursor-pointer" onClick={() => navigate('/dashboard')}>
                CV Verification
              </span>
              {(user?.role === 'recruiter' || user?.role === 'admin') && (
                <button onClick={() => navigate('/upload')} className="text-sm text-gray-600 hover:text-gray-900">
                  Upload CV
                </button>
              )}
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500">{user?.full_name}</span>
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full capitalize">{user?.role}</span>
              <button onClick={handleLogout} className="text-sm text-gray-500 hover:text-gray-900">Sign out</button>
            </div>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">{children}</main>
    </div>
  )
}