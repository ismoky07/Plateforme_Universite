import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { useUIStore } from '../../store/uiStore'
import { Menu, LogOut, User, Bell } from 'lucide-react'

export default function Header() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const { toggleSidebar } = useUIStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const getRoleBadge = () => {
    switch (user?.role) {
      case 'admin':
        return <span className="badge badge-error">Admin</span>
      case 'professor':
        return <span className="badge badge-primary">Professeur</span>
      case 'student':
        return <span className="badge badge-success">Etudiant</span>
      default:
        return null
    }
  }

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      {/* Left side */}
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <Menu size={20} />
        </button>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {/* Notifications */}
        <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors relative">
          <Bell size={20} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        {/* User info */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <p className="text-sm font-medium text-gray-900">
              {user?.full_name || user?.username}
            </p>
            {getRoleBadge()}
          </div>

          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
            <User size={20} className="text-primary-600" />
          </div>

          <button
            onClick={handleLogout}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-600"
            title="Deconnexion"
          >
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </header>
  )
}
