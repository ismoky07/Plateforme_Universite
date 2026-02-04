import { NavLink, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { useUIStore } from '../../store/uiStore'
import {
  Home,
  FileText,
  Upload,
  CheckSquare,
  BarChart2,
  Users,
  Settings,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  ClipboardList,
  PenTool,
} from 'lucide-react'

interface NavItem {
  path: string
  label: string
  icon: React.ReactNode
}

export default function Sidebar() {
  const { user } = useAuthStore()
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const location = useLocation()

  // Navigation items based on role
  const getNavItems = (): NavItem[] => {
    switch (user?.role) {
      case 'student':
        return [
          { path: '/student', label: 'Tableau de bord', icon: <Home size={20} /> },
          { path: '/student/exams', label: 'Examens disponibles', icon: <BookOpen size={20} /> },
          { path: '/student/submit', label: 'Soumettre une copie', icon: <Upload size={20} /> },
          { path: '/student/submissions', label: 'Mes soumissions', icon: <FileText size={20} /> },
          { path: '/student/results', label: 'Mes resultats', icon: <BarChart2 size={20} /> },
        ]
      case 'professor':
        return [
          { path: '/professor', label: 'Tableau de bord', icon: <Home size={20} /> },
          { path: '/professor/evaluations/new', label: 'Creer evaluation', icon: <PenTool size={20} /> },
          { path: '/professor/copies', label: 'Gerer les copies', icon: <FileText size={20} /> },
          { path: '/professor/correction', label: 'Lancer correction', icon: <CheckSquare size={20} /> },
          { path: '/professor/reports', label: 'Voir resultats', icon: <BarChart2 size={20} /> },
        ]
      case 'admin':
        return [
          { path: '/admin', label: 'Tableau de bord', icon: <Home size={20} /> },
          { path: '/admin/candidatures', label: 'Candidatures', icon: <ClipboardList size={20} /> },
          { path: '/admin/users', label: 'Utilisateurs', icon: <Users size={20} /> },
        ]
      default:
        return []
    }
  }

  const navItems = getNavItems()

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-50 bg-white border-r border-gray-200 transition-all duration-300 ${
        sidebarOpen ? 'w-64' : 'w-20'
      } hidden lg:block`}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
        {sidebarOpen && (
          <h1 className="text-xl font-bold text-primary-600">Universite</h1>
        )}
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          {sidebarOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/student' || item.path === '/professor' || item.path === '/admin'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-600'
                  : 'text-gray-600 hover:bg-gray-100'
              }`
            }
          >
            {item.icon}
            {sidebarOpen && <span className="font-medium">{item.label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
