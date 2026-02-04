import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { evaluationsApi } from '../../api/evaluations'
import { reportsApi, StudentReport } from '../../api/reports'
import Card, { CardHeader, CardTitle, CardContent } from '../../components/common/Card'
import MetricCard from '../../components/common/MetricCard'
import StatusBadge from '../../components/common/StatusBadge'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import Button from '../../components/common/Button'
import { Evaluation } from '../../types/evaluation'
import { BookOpen, FileText, BarChart2, Clock, ArrowRight } from 'lucide-react'

export default function StudentDashboard() {
  const { user } = useAuthStore()
  const [evaluations, setEvaluations] = useState<Evaluation[]>([])
  const [reports, setReports] = useState<StudentReport[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [evalsData, reportsData] = await Promise.all([
        evaluationsApi.listAvailable(),
        reportsApi.getMyReports().catch(() => []),
      ])
      setEvaluations(evalsData)
      setReports(reportsData)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Chargement..." />
  }

  const openEvals = evaluations.filter((e) => e.statut === 'ouvert')
  const avgNote = reports.length > 0
    ? (reports.reduce((sum, r) => sum + (r.note / r.note_max) * 20, 0) / reports.length).toFixed(1)
    : '-'

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Bonjour, {user?.prenom || user?.full_name}!
        </h1>
        <p className="text-gray-600 mt-1">
          Bienvenue sur votre espace etudiant
        </p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Examens disponibles"
          value={openEvals.length}
          icon={<BookOpen size={24} />}
          color="primary"
        />
        <MetricCard
          label="Copies soumises"
          value={reports.length}
          icon={<FileText size={24} />}
          color="success"
        />
        <MetricCard
          label="Resultats publies"
          value={reports.filter((r) => r.has_pdf).length}
          icon={<BarChart2 size={24} />}
          color="warning"
        />
        <MetricCard
          label="Moyenne generale"
          value={avgNote}
          icon={<BarChart2 size={24} />}
          color="default"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Available Exams */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Examens disponibles</CardTitle>
              <Link to="/student/exams">
                <Button variant="ghost" size="sm" rightIcon={<ArrowRight size={16} />}>
                  Voir tous
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {openEvals.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                Aucun examen disponible pour le moment
              </p>
            ) : (
              <div className="space-y-3">
                {openEvals.slice(0, 3).map((exam) => (
                  <div
                    key={exam.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <h4 className="font-medium text-gray-900">{exam.titre}</h4>
                      <p className="text-sm text-gray-500">
                        {exam.matiere} - {exam.classe}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right text-sm text-gray-500">
                        <Clock size={14} className="inline mr-1" />
                        {exam.duree_minutes} min
                      </div>
                      <StatusBadge status={exam.statut} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Results */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Derniers resultats</CardTitle>
              <Link to="/student/results">
                <Button variant="ghost" size="sm" rightIcon={<ArrowRight size={16} />}>
                  Voir tous
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {reports.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                Aucun resultat disponible
              </p>
            ) : (
              <div className="space-y-3">
                {reports.slice(0, 3).map((report) => (
                  <div
                    key={report.evaluation_id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <h4 className="font-medium text-gray-900">
                        {report.evaluation_titre}
                      </h4>
                      <p className="text-sm text-gray-500">{report.matiere}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold text-gray-900">
                        {report.note}/{report.note_max}
                      </p>
                      <p className="text-sm text-gray-500">
                        {((report.note / report.note_max) * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
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
            <Link to="/student/exams">
              <Button leftIcon={<BookOpen size={18} />}>
                Voir les examens
              </Button>
            </Link>
            <Link to="/student/submit">
              <Button variant="secondary" leftIcon={<FileText size={18} />}>
                Soumettre une copie
              </Button>
            </Link>
            <Link to="/student/results">
              <Button variant="secondary" leftIcon={<BarChart2 size={18} />}>
                Mes resultats
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
