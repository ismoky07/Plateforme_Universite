import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { evaluationsApi } from '../../api/evaluations'
import Card, { CardHeader, CardTitle, CardContent } from '../../components/common/Card'
import MetricCard from '../../components/common/MetricCard'
import StatusBadge from '../../components/common/StatusBadge'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import Button from '../../components/common/Button'
import { Evaluation } from '../../types/evaluation'
import {
  FileText,
  CheckCircle,
  Clock,
  Users,
  Plus,
  ArrowRight,
  AlertTriangle,
} from 'lucide-react'

export default function ProfessorDashboard() {
  const { user } = useAuthStore()
  const [evaluations, setEvaluations] = useState<Evaluation[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadEvaluations()
  }, [])

  const loadEvaluations = async () => {
    try {
      const data = await evaluationsApi.list()
      setEvaluations(data)
    } catch (error) {
      console.error('Error loading evaluations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Chargement..." />
  }

  const openEvals = evaluations.filter((e) => e.statut === 'ouvert')
  const closedEvals = evaluations.filter((e) => e.statut === 'ferme')
  const publishedEvals = evaluations.filter((e) => e.statut_publication === 'publie')
  const totalCopies = evaluations.reduce((sum, e) => sum + e.nombre_copies, 0)

  // Alerts
  const alerts = []
  if (openEvals.length > 0) {
    alerts.push({
      type: 'info',
      message: `${openEvals.length} evaluation(s) en cours de reception`,
    })
  }
  const needsCorrection = closedEvals.filter((e) => e.nombre_corriges < e.nombre_copies)
  if (needsCorrection.length > 0) {
    alerts.push({
      type: 'warning',
      message: `${needsCorrection.length} evaluation(s) en attente de correction`,
    })
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Bonjour, {user?.full_name}!
          </h1>
          <p className="text-gray-600 mt-1">Tableau de bord professeur</p>
        </div>
        <Link to="/professor/evaluations/new">
          <Button leftIcon={<Plus size={18} />}>Nouvelle evaluation</Button>
        </Link>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          {alerts.map((alert, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg flex items-center gap-3 ${
                alert.type === 'warning'
                  ? 'bg-yellow-50 text-yellow-800'
                  : 'bg-blue-50 text-blue-800'
              }`}
            >
              <AlertTriangle size={20} />
              {alert.message}
            </div>
          ))}
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Evaluations creees"
          value={evaluations.length}
          icon={<FileText size={24} />}
          color="primary"
        />
        <MetricCard
          label="En cours"
          value={openEvals.length}
          icon={<Clock size={24} />}
          color="warning"
        />
        <MetricCard
          label="Publiees"
          value={publishedEvals.length}
          icon={<CheckCircle size={24} />}
          color="success"
        />
        <MetricCard
          label="Copies recues"
          value={totalCopies}
          icon={<Users size={24} />}
          color="default"
        />
      </div>

      {/* Recent Evaluations */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Mes evaluations</CardTitle>
            <Button variant="ghost" size="sm" rightIcon={<ArrowRight size={16} />}>
              Voir toutes
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {evaluations.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Aucune evaluation creee</p>
              <Link to="/professor/evaluations/new">
                <Button className="mt-4" leftIcon={<Plus size={18} />}>
                  Creer ma premiere evaluation
                </Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {evaluations.slice(0, 5).map((eval_) => (
                <div
                  key={eval_.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <h4 className="font-medium text-gray-900">{eval_.titre}</h4>
                      <StatusBadge status={eval_.statut} />
                      <StatusBadge status={eval_.statut_publication} />
                    </div>
                    <p className="text-sm text-gray-500">
                      {eval_.matiere} - {eval_.classe} |{' '}
                      {eval_.nombre_copies} copies | {eval_.nombre_corriges} corrigees
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Link to={`/professor/copies?eval=${eval_.id}`}>
                      <Button variant="ghost" size="sm">
                        Copies
                      </Button>
                    </Link>
                    {eval_.statut === 'ferme' && eval_.nombre_copies > 0 && (
                      <Link to={`/professor/correction?eval=${eval_.id}`}>
                        <Button size="sm">Corriger</Button>
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Actions rapides</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Link to="/professor/evaluations/new">
              <Button leftIcon={<Plus size={18} />}>Nouvelle evaluation</Button>
            </Link>
            <Link to="/professor/copies">
              <Button variant="secondary" leftIcon={<FileText size={18} />}>
                Gerer les copies
              </Button>
            </Link>
            <Link to="/professor/correction">
              <Button variant="secondary" leftIcon={<CheckCircle size={18} />}>
                Lancer correction
              </Button>
            </Link>
            <Link to="/professor/reports">
              <Button variant="secondary" leftIcon={<Users size={18} />}>
                Voir resultats
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
