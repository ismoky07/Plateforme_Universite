import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'

// Layout
import MainLayout from './components/layout/MainLayout'
import ProtectedRoute from './components/layout/ProtectedRoute'

// Auth Pages
import LoginPage from './pages/auth/LoginPage'

// Student Pages
import StudentDashboard from './pages/student/DashboardPage'
import AvailableExamsPage from './pages/student/AvailableExamsPage'
import SubmitCopyPage from './pages/student/SubmitCopyPage'
import MySubmissionsPage from './pages/student/MySubmissionsPage'
import MyResultsPage from './pages/student/MyResultsPage'

// Professor Pages
import ProfessorDashboard from './pages/professor/DashboardPage'
import CreateEvaluationPage from './pages/professor/CreateEvaluationPage'
import ManageCopiesPage from './pages/professor/ManageCopiesPage'
import LaunchCorrectionPage from './pages/professor/LaunchCorrectionPage'
import ViewReportsPage from './pages/professor/ViewReportsPage'

// Admin Pages
import AdminDashboard from './pages/admin/DashboardPage'
import CandidaturesPage from './pages/admin/CandidaturesPage'
import UsersPage from './pages/admin/UsersPage'

// Candidature Page
import ApplicationFormPage from './pages/candidature/ApplicationFormPage'

function App() {
  const { isAuthenticated, user } = useAuthStore()

  // Determine default route based on user role
  const getDefaultRoute = () => {
    if (!isAuthenticated) return '/login'
    switch (user?.role) {
      case 'admin':
        return '/admin'
      case 'professor':
        return '/professor'
      case 'student':
        return '/student'
      default:
        return '/login'
    }
  }

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/candidature" element={<ApplicationFormPage />} />

      {/* Student Routes */}
      <Route
        path="/student"
        element={
          <ProtectedRoute allowedRoles={['student', 'admin']}>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<StudentDashboard />} />
        <Route path="exams" element={<AvailableExamsPage />} />
        <Route path="submit" element={<SubmitCopyPage />} />
        <Route path="submissions" element={<MySubmissionsPage />} />
        <Route path="results" element={<MyResultsPage />} />
      </Route>

      {/* Professor Routes */}
      <Route
        path="/professor"
        element={
          <ProtectedRoute allowedRoles={['professor', 'admin']}>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<ProfessorDashboard />} />
        <Route path="evaluations/new" element={<CreateEvaluationPage />} />
        <Route path="copies" element={<ManageCopiesPage />} />
        <Route path="correction" element={<LaunchCorrectionPage />} />
        <Route path="reports" element={<ViewReportsPage />} />
      </Route>

      {/* Admin Routes */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<AdminDashboard />} />
        <Route path="candidatures" element={<CandidaturesPage />} />
        <Route path="users" element={<UsersPage />} />
      </Route>

      {/* Default Route */}
      <Route path="/" element={<Navigate to={getDefaultRoute()} replace />} />
      <Route path="*" element={<Navigate to={getDefaultRoute()} replace />} />
    </Routes>
  )
}

export default App
