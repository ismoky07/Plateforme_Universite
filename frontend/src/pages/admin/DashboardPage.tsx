import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { candidaturesApi } from '../../api/candidatures'
import { evaluationsApi } from '../../api/evaluations'
import Card, { CardHeader, CardTitle, CardContent } from '../../components/common/Card'
import MetricCard from '../../components/common/MetricCard'
import StatusBadge from '../../components/common/StatusBadge'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import Button from '../../components/common/Button'
import { Candidature } from '../../types/candidature'
import { Evaluation } from '../../types/evaluation'
import {
  Users,
  FileText,
  CheckCircle,
  Clock,
  ArrowRight,
  ClipboardList,
} from 'lucide-react'

export default function AdminDashboard() {
  const { user } = useAuthStore()
  const [candidatures, setCandidatures] = useState<Candidature[]>([])
  const [evaluations, setEvaluations] = useState<Evaluation[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [candData, evalData] = await Promise.all([
        candidaturesApi.list().catch(() => []),
        evaluationsApi.list().catch(() => []),
      ])
      setCandidatures(candData)
      setEvaluations(evalData)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Chargement..." />
  }

  const pendingCandidatures = candidatures.filter((c) => c.statut === 'en_attente')
  const validatedCandidatures = candidatures.filter((c) => c.statut === 'validee')
  const totalCopies = evaluations.reduce((sum, e) => sum + e.nombre_copies, 0)

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Administration
        </h1>
        <p className="text-gray-600 mt-1">
          Bienvenue, {user?.full_name}
        </p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Candidatures totales"
          value={candidatures.length}
          icon={<ClipboardList size={24} />}
          color="primary"
        />
        <MetricCard
          label="En attente"
          value={pendingCandidatures.length}
          icon={<Clock size={24} />}
          color="warning"
        />
        <MetricCard
          label="Validees"
          value={validatedCandidatures.length}
          icon={<CheckCircle size={24} />}
          color="success"
        />
        <MetricCard
          label="Evaluations"
          value={evaluations.length}
          icon={<FileText size={24} />}
          color="default"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Candidatures */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Candidatures recentes</CardTitle>
              <Link to="/admin/candidatures">
                <Button variant="ghost" size="sm" rightIcon={<ArrowRight size={16} />}>
                  Voir toutes
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {candidatures.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                Aucune candidature
              </p>
            ) : (
              <div className="space-y-3">
                {candidatures.slice(0, 5).map((cand) => (
                  <div
                    key={cand.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <h4 className="font-medium text-gray-900">
                        {cand.personal_info.prenom} {cand.personal_info.nom}
                      </h4>
                      <p className="text-sm text-gray-500">
                        {cand.personal_info.niveau_etude} | {cand.personal_info.email}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      {cand.moyenne_generale && (
                        <span className="text-sm font-medium">
                          {cand.moyenne_generale.toFixed(1)}/20
                        </span>
                      )}
                      <StatusBadge status={cand.statut} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* System Stats */}
        <Card>
          <CardHeader>
            <CardTitle>Statistiques systeme</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Evaluations actives</span>
                <span className="font-semibold">
                  {evaluations.filter((e) => e.statut === 'ouvert').length}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Copies totales</span>
                <span className="font-semibold">{totalCopies}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Taux de validation</span>
                <span className="font-semibold">
                  {candidatures.length > 0
                    ? ((validatedCandidatures.length / candidatures.length) * 100).toFixed(0)
                    : 0}
                  %
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Candidatures ce mois</span>
                <span className="font-semibold">
                  {candidatures.filter((c) => {
                    const date = new Date(c.date_soumission)
                    const now = new Date()
                    return (
                      date.getMonth() === now.getMonth() &&
                      date.getFullYear() === now.getFullYear()
                    )
                  }).length}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Actions rapides</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Link to="/admin/candidatures">
              <Button leftIcon={<ClipboardList size={18} />}>
                Gerer candidatures
              </Button>
            </Link>
            <Link to="/admin/users">
              <Button variant="secondary" leftIcon={<Users size={18} />}>
                Gerer utilisateurs
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
