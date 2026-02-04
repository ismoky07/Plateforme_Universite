import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { evaluationsApi } from '../../api/evaluations'
import { submissionsApi } from '../../api/submissions'
import { useToast } from '../../store/uiStore'
import Card, { CardHeader, CardTitle, CardContent } from '../../components/common/Card'
import MetricCard from '../../components/common/MetricCard'
import Button from '../../components/common/Button'
import Select from '../../components/common/Form/Select'
import StatusBadge from '../../components/common/StatusBadge'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { Evaluation } from '../../types/evaluation'
import { Submission } from '../../types/submission'
import { FileText, Upload, Trash2, RefreshCw, Eye } from 'lucide-react'

export default function ManageCopiesPage() {
  const [searchParams] = useSearchParams()
  const toast = useToast()

  const [evaluations, setEvaluations] = useState<Evaluation[]>([])
  const [selectedEval, setSelectedEval] = useState<string>(searchParams.get('eval') || '')
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingSubmissions, setIsLoadingSubmissions] = useState(false)

  useEffect(() => {
    loadEvaluations()
  }, [])

  useEffect(() => {
    if (selectedEval) {
      loadSubmissions()
    }
  }, [selectedEval])

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

  const loadSubmissions = async () => {
    setIsLoadingSubmissions(true)
    try {
      const data = await submissionsApi.listByEvaluation(selectedEval)
      setSubmissions(data)
    } catch (error) {
      console.error('Error loading submissions:', error)
    } finally {
      setIsLoadingSubmissions(false)
    }
  }

  const handleDeleteSubmission = async (submissionId: string) => {
    if (!confirm('Supprimer cette soumission?')) return

    try {
      await submissionsApi.delete(submissionId, selectedEval)
      toast.success('Soumission supprimee')
      loadSubmissions()
    } catch (error) {
      toast.error('Erreur lors de la suppression')
    }
  }

  const handleOpenEvaluation = async () => {
    try {
      await evaluationsApi.open(selectedEval)
      toast.success('Evaluation ouverte aux soumissions')
      loadEvaluations()
    } catch (error) {
      toast.error('Erreur')
    }
  }

  const handleCloseEvaluation = async () => {
    try {
      await evaluationsApi.close(selectedEval)
      toast.success('Evaluation fermee')
      loadEvaluations()
    } catch (error) {
      toast.error('Erreur')
    }
  }

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Chargement..." />
  }

  const selectedEvaluation = evaluations.find((e) => e.id === selectedEval)
  const totalSize = submissions.reduce((sum, s) => sum + s.taille_totale, 0)
  const correctedCount = submissions.filter((s) => s.corrige).length

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Gestion des copies</h1>
        <p className="text-gray-600 mt-1">
          Visualisez et gerez les copies soumises par les etudiants
        </p>
      </div>

      {/* Evaluation Selection */}
      <Card>
        <CardContent>
          <div className="flex items-end gap-4">
            <div className="flex-1">
              <Select
                label="Selectionnez une evaluation"
                value={selectedEval}
                onChange={(e) => setSelectedEval(e.target.value)}
                options={evaluations.map((e) => ({
                  value: e.id,
                  label: `${e.titre} - ${e.matiere} (${e.nombre_copies} copies)`,
                }))}
                placeholder="Choisir une evaluation..."
              />
            </div>
            <Button
              variant="secondary"
              onClick={loadSubmissions}
              disabled={!selectedEval}
              leftIcon={<RefreshCw size={18} />}
            >
              Actualiser
            </Button>
          </div>
        </CardContent>
      </Card>

      {selectedEvaluation && (
        <>
          {/* Evaluation Info & Actions */}
          <Card>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{selectedEvaluation.titre}</h3>
                  <div className="flex items-center gap-3 mt-1">
                    <StatusBadge status={selectedEvaluation.statut} />
                    <span className="text-sm text-gray-500">
                      {selectedEvaluation.matiere} - {selectedEvaluation.classe}
                    </span>
                  </div>
                </div>
                <div className="flex gap-2">
                  {selectedEvaluation.statut === 'brouillon' || selectedEvaluation.statut === 'ferme' ? (
                    <Button
                      variant="success"
                      onClick={handleOpenEvaluation}
                    >
                      Ouvrir aux soumissions
                    </Button>
                  ) : (
                    <Button
                      variant="secondary"
                      onClick={handleCloseEvaluation}
                    >
                      Fermer
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <MetricCard
              label="Copies recues"
              value={submissions.length}
              icon={<FileText size={24} />}
              color="primary"
            />
            <MetricCard
              label="Corrigees"
              value={correctedCount}
              icon={<FileText size={24} />}
              color="success"
            />
            <MetricCard
              label="En attente"
              value={submissions.length - correctedCount}
              icon={<FileText size={24} />}
              color="warning"
            />
            <MetricCard
              label="Taille totale"
              value={`${(totalSize / 1024 / 1024).toFixed(1)} MB`}
              icon={<Upload size={24} />}
              color="default"
            />
          </div>

          {/* Submissions List */}
          <Card>
            <CardHeader>
              <CardTitle>Copies soumises ({submissions.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoadingSubmissions ? (
                <LoadingSpinner text="Chargement des copies..." />
              ) : submissions.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Aucune copie soumise</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {submissions.map((submission) => (
                    <div
                      key={submission.id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                    >
                      <div>
                        <h4 className="font-medium text-gray-900">
                          {submission.etudiant_prenom} {submission.etudiant_nom}
                        </h4>
                        <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                          <span>
                            {new Date(submission.date_soumission).toLocaleDateString('fr-FR')}{' '}
                            {new Date(submission.date_soumission).toLocaleTimeString('fr-FR', {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </span>
                          <span>{submission.nombre_fichiers} fichier(s)</span>
                          <span>
                            {(submission.taille_totale / 1024 / 1024).toFixed(2)} MB
                          </span>
                          <StatusBadge status={submission.statut} />
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="ghost" size="sm" leftIcon={<Eye size={16} />}>
                          Voir
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteSubmission(submission.id)}
                        >
                          <Trash2 size={16} className="text-red-500" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
