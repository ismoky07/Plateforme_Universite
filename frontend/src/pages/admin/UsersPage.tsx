import { useEffect, useState } from 'react'
import Card, { CardHeader, CardTitle, CardContent } from '../../components/common/Card'
import MetricCard from '../../components/common/MetricCard'
import Button from '../../components/common/Button'
import StatusBadge from '../../components/common/StatusBadge'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { Users, UserPlus, Shield, User } from 'lucide-react'

interface UserData {
  username: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
}

export default function UsersPage() {
  const [users, setUsers] = useState<UserData[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulated data - in production, call the API
    setUsers([
      {
        username: 'admin',
        email: 'admin@universite.fr',
        full_name: 'Administrateur',
        role: 'admin',
        is_active: true,
        created_at: '2024-01-01',
      },
      {
        username: 'prof',
        email: 'prof@universite.fr',
        full_name: 'Professeur Martin',
        role: 'professor',
        is_active: true,
        created_at: '2024-01-15',
      },
    ])
    setIsLoading(false)
  }, [])

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Chargement..." />
  }

  const adminCount = users.filter((u) => u.role === 'admin').length
  const profCount = users.filter((u) => u.role === 'professor').length
  const activeCount = users.filter((u) => u.is_active).length

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin':
        return <Shield size={16} className="text-red-500" />
      case 'professor':
        return <User size={16} className="text-blue-500" />
      default:
        return <User size={16} className="text-gray-500" />
    }
  }

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'admin':
        return <span className="badge bg-red-50 text-red-700">Admin</span>
      case 'professor':
        return <span className="badge bg-blue-50 text-blue-700">Professeur</span>
      default:
        return <span className="badge bg-gray-50 text-gray-700">{role}</span>
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Utilisateurs</h1>
          <p className="text-gray-600 mt-1">
            Gestion des comptes utilisateurs
          </p>
        </div>
        <Button leftIcon={<UserPlus size={18} />}>
          Nouvel utilisateur
        </Button>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          label="Total utilisateurs"
          value={users.length}
          icon={<Users size={24} />}
          color="primary"
        />
        <MetricCard
          label="Administrateurs"
          value={adminCount}
          icon={<Shield size={24} />}
          color="error"
        />
        <MetricCard
          label="Professeurs"
          value={profCount}
          icon={<User size={24} />}
          color="primary"
        />
        <MetricCard
          label="Comptes actifs"
          value={activeCount}
          icon={<Users size={24} />}
          color="success"
        />
      </div>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>Liste des utilisateurs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                    Utilisateur
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                    Email
                  </th>
                  <th className="text-center py-3 px-4 text-sm font-medium text-gray-500">
                    Role
                  </th>
                  <th className="text-center py-3 px-4 text-sm font-medium text-gray-500">
                    Statut
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr
                    key={user.username}
                    className="border-b border-gray-100 hover:bg-gray-50"
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                          {getRoleIcon(user.role)}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{user.full_name}</p>
                          <p className="text-sm text-gray-500">@{user.username}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-600">{user.email}</td>
                    <td className="py-3 px-4 text-center">{getRoleBadge(user.role)}</td>
                    <td className="py-3 px-4 text-center">
                      {user.is_active ? (
                        <span className="badge bg-green-50 text-green-700">Actif</span>
                      ) : (
                        <span className="badge bg-gray-50 text-gray-700">Inactif</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Button variant="ghost" size="sm">
                        Modifier
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
