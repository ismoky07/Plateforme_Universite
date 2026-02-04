import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { evaluationsApi } from '../../api/evaluations'
import Card from '../../components/common/Card'
import StatusBadge from '../../components/common/StatusBadge'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import Button from '../../components/common/Button'
import { Evaluation } from '../../types/evaluation'
import { Clock, Calendar, User, FileText } from 'lucide-react'

export default function AvailableExamsPage() {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadEvaluations()
  }, [])

  const loadEvaluations = async () => {
    try {
      const data = await evaluationsApi.listAvailable()
      setEvaluations(data)
    } catch (error) {
      console.error('Error loading evaluations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Chargement des examens..." />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Examens disponibles</h1>
          <p className="text-gray-600 mt-1">
            {evaluations.length} examen(s) ouvert(s) aux soumissions
          </p>
        </div>
        <Button onClick={loadEvaluations} variant="secondary">
          Actualiser
        </Button>
      </div>

      {evaluations.length === 0 ? (
        <Card className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900">Aucun examen disponible</h3>
          <p className="text-gray-500 mt-1">
            Revenez plus tard pour voir les nouveaux examens
          </p>
        </Card>
      ) : (
        <div className="grid gap-4">
          {evaluations.map((exam) => (
            <Card key={exam.id} className="hover:shadow-md transition-shadow">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {exam.titre}
                    </h3>
                    <StatusBadge status={exam.statut} />
                  </div>

                  <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      <FileText size={16} />
                      {exam.matiere}
                    </span>
                    <span className="flex items-center gap-1">
                      <User size={16} />
                      {exam.classe}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock size={16} />
                      {exam.duree_minutes} minutes
                    </span>
                    {exam.date_examen && (
                      <span className="flex items-center gap-1">
                        <Calendar size={16} />
                        {new Date(exam.date_examen).toLocaleDateString('fr-FR')}
                      </span>
                    )}
                  </div>

                  {exam.consignes_specifiques && (
                    <p className="mt-3 text-sm text-gray-500">
                      {exam.consignes_specifiques}
                    </p>
                  )}
                </div>

                <div className="flex flex-col items-end gap-2">
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Note maximale</p>
                    <p className="text-xl font-semibold text-gray-900">
                      {exam.note_totale} pts
                    </p>
                  </div>

                  <Link to={`/student/submit?eval=${exam.id}`}>
                    <Button>Soumettre ma copie</Button>
                  </Link>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
