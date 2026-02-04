import { useEffect, useState } from 'react'
import { useAuthStore } from '../../store/authStore'
import Card from '../../components/common/Card'
import MetricCard from '../../components/common/MetricCard'
import StatusBadge from '../../components/common/StatusBadge'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { FileText, CheckCircle, Clock, Upload } from 'lucide-react'

interface SubmissionDisplay {
  id: string
  evaluation_titre: string
  matiere: string
  date_soumission: string
  type_soumission: string
  statut: string
  nombre_fichiers: number
  corrige: boolean
  note_finale?: number
}

export default function MySubmissionsPage() {
  const { user } = useAuthStore()
  const [submissions, setSubmissions] = useState<SubmissionDisplay[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // In a real app, this would call an API to get student's submissions
    // For now, we'll show a placeholder
    setIsLoading(false)
  }, [user])

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Chargement..." />
  }

  const correctedCount = submissions.filter((s) => s.corrige).length
  const pendingCount = submissions.filter((s) => !s.corrige).length

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Mes soumissions</h1>
        <p className="text-gray-600 mt-1">
          Historique de vos copies soumises
        </p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          label="Total soumissions"
          value={submissions.length}
          icon={<Upload size={24} />}
          color="primary"
        />
        <MetricCard
          label="Corrigees"
          value={correctedCount}
          icon={<CheckCircle size={24} />}
          color="success"
        />
        <MetricCard
          label="En attente"
          value={pendingCount}
          icon={<Clock size={24} />}
          color="warning"
        />
      </div>

      {/* Submissions List */}
      {submissions.length === 0 ? (
        <Card className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900">Aucune soumission</h3>
          <p className="text-gray-500 mt-1">
            Vous n'avez pas encore soumis de copie
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {submissions.map((submission) => (
            <Card key={submission.id}>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-gray-900">
                      {submission.evaluation_titre}
                    </h3>
                    <StatusBadge status={submission.statut} />
                  </div>
                  <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                    <span>{submission.matiere}</span>
                    <span>
                      Soumis le{' '}
                      {new Date(submission.date_soumission).toLocaleDateString('fr-FR')}
                    </span>
                    <span>{submission.nombre_fichiers} fichier(s)</span>
                  </div>
                </div>

                <div className="text-right">
                  {submission.corrige && submission.note_finale !== undefined ? (
                    <div>
                      <p className="text-2xl font-bold text-gray-900">
                        {submission.note_finale}/20
                      </p>
                      <p className="text-sm text-gray-500">Note finale</p>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">En attente de correction</p>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
