import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import Button from '../../components/common/Button'
import Input from '../../components/common/Form/Input'
import Card from '../../components/common/Card'
import AlertBox from '../../components/common/AlertBox'
import { GraduationCap } from 'lucide-react'

type LoginMode = 'professor' | 'student'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, studentLogin, isLoading, error, clearError } = useAuthStore()

  const [mode, setMode] = useState<LoginMode>('student')

  // Professor login form
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  // Student login form
  const [numeroEtudiant, setNumeroEtudiant] = useState('')
  const [nom, setNom] = useState('')
  const [prenom, setPrenom] = useState('')

  const handleProfessorLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()

    try {
      await login(username, password)
      navigate('/professor')
    } catch {
      // Error is handled by store
    }
  }

  const handleStudentLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()

    try {
      await studentLogin(numeroEtudiant, nom, prenom)
      navigate('/student')
    } catch {
      // Error is handled by store
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4">
            <GraduationCap className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Plateforme Universite</h1>
          <p className="text-gray-600 mt-1">Connectez-vous pour acceder a votre espace</p>
        </div>

        <Card>
          {/* Mode Toggle */}
          <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
            <button
              type="button"
              onClick={() => {
                setMode('student')
                clearError()
              }}
              className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
                mode === 'student'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Etudiant
            </button>
            <button
              type="button"
              onClick={() => {
                setMode('professor')
                clearError()
              }}
              className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
                mode === 'professor'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Professeur / Admin
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <AlertBox
              type="error"
              message={error}
              onClose={clearError}
              className="mb-4"
            />
          )}

          {/* Student Login Form */}
          {mode === 'student' && (
            <form onSubmit={handleStudentLogin} className="space-y-4">
              <Input
                label="Numero etudiant"
                value={numeroEtudiant}
                onChange={(e) => setNumeroEtudiant(e.target.value)}
                placeholder="Ex: 12345678"
                required
              />
              <Input
                label="Nom"
                value={nom}
                onChange={(e) => setNom(e.target.value)}
                placeholder="Votre nom de famille"
                required
              />
              <Input
                label="Prenom"
                value={prenom}
                onChange={(e) => setPrenom(e.target.value)}
                placeholder="Votre prenom"
                required
              />
              <Button
                type="submit"
                className="w-full"
                isLoading={isLoading}
              >
                Se connecter
              </Button>
            </form>
          )}

          {/* Professor/Admin Login Form */}
          {mode === 'professor' && (
            <form onSubmit={handleProfessorLogin} className="space-y-4">
              <Input
                label="Nom d'utilisateur"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Votre identifiant"
                required
              />
              <Input
                label="Mot de passe"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Votre mot de passe"
                required
              />
              <Button
                type="submit"
                className="w-full"
                isLoading={isLoading}
              >
                Se connecter
              </Button>

              {/* Demo credentials hint */}
              <p className="text-xs text-gray-500 text-center mt-4">
                Demo: admin/admin123 ou prof/prof123
              </p>
            </form>
          )}
        </Card>

        {/* Candidature Link */}
        <p className="text-center mt-6 text-gray-600">
          Nouveau candidat?{' '}
          <a href="/candidature" className="text-primary-600 hover:underline font-medium">
            Deposer une candidature
          </a>
        </p>
      </div>
    </div>
  )
}
