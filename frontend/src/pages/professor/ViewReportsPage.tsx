import { useEffect, useState } from 'react'
import { evaluationsApi } from '../../api/evaluations'
import { correctionsApi } from '../../api/corrections'
import { useToast } from '../../store/uiStore'
import Card, { CardHeader, CardTitle, CardContent } from '../../components/common/Card'
import MetricCard from '../../components/common/MetricCard'
import Button from '../../components/common/Button'
import Select from '../../components/common/Form/Select'
import StatusBadge from '../../components/common/StatusBadge'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { Evaluation } from '../../types/evaluation'
import { CorrectionResult, ClassStatistics } from '../../types/correction'
import {
  BarChart2,
  Users,
  TrendingUp,
  Download,
  Eye,
  EyeOff,
  RefreshCw,
} from 'lucide-react'

export default function ViewReportsPage() {
  const toast = useToast()

  const [evaluations, setEvaluations] = useState<Evaluation[]>([])
  const [selectedEval, setSelectedEval] = useState<string>('')
  const [results, setResults] = useState<CorrectionResult[]>([])
  const [statistics, setStatistics] = useState<ClassStatistics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingResults, setIsLoadingResults] = useState(false)

  useEffect(() => {
    loadEvaluations()
  }, [])

  useEffect(() => {
    if (selectedEval) {
      loadResults()
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

  const loadResults = async () => {
    setIsLoadingResults(true)
    try {
      const [resultsData, statsData] = await Promise.all([
        correctionsApi.getResults(selectedEval),
        correctionsApi.getStatistics(selectedEval).catch(() => null),
      ])
      setResults(resultsData)
      setStatistics(statsData)
    } catch (error) {
      console.error('Error loading results:', error)
    } finally {
      setIsLoadingResults(false)
    }
  }

  const handlePublish = async () => {
    try {
      await evaluationsApi.publish(selectedEval, { notify_students: true })
      toast.success('Resultats publies!')
      loadEvaluations()
    } catch (error) {
      toast.error('Erreur lors de la publication')
    }
  }

  const handleUnpublish = async () => {
    try {
      await evaluationsApi.unpublish(selectedEval)
      toast.success('Resultats depublies')
      loadEvaluations()
    } catch (error) {
      toast.error('Erreur')
    }
  }

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Chargement..." />
  }

  const selectedEvaluation = evaluations.find((e) => e.id === selectedEval)
  const isPublished = selectedEvaluation?.statut_publication === 'publie'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Resultats et rapports</h1>
        <p className="text-gray-600 mt-1">
          Consultez les resultats et publiez-les aux etudiants
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
                  label: `${e.titre} - ${e.matiere} (${e.nombre_corriges}/${e.nombre_copies} corrigees)`,
                }))}
                placeholder="Choisir une evaluation..."
              />
            </div>
            <Button
              variant="secondary"
              onClick={loadResults}
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
          {/* Publication Status */}
          <Card>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{selectedEvaluation.titre}</h3>
                  <div className="flex items-center gap-3 mt-1">
                    <StatusBadge status={selectedEvaluation.statut_publication} />
                    <span className="text-sm text-gray-500">
                      {results.length} resultats disponibles
                    </span>
                  </div>
                </div>
                <div className="flex gap-2">
                  {isPublished ? (
                    <Button
                      variant="secondary"
                      onClick={handleUnpublish}
                      leftIcon={<EyeOff size={18} />}
                    >
                      Depublier
                    </Button>
                  ) : (
                    <Button
                      variant="success"
                      onClick={handlePublish}
                      disabled={results.length === 0}
                      leftIcon={<Eye size={18} />}
                    >
                      Publier les resultats
                    </Button>
                  )}
                  <Button variant="secondary" leftIcon={<Download size={18} />}>
                    Exporter
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Statistics */}
          {statistics && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <MetricCard
                label="Moyenne"
                value={statistics.moyenne_generale.toFixed(1)}
                icon={<BarChart2 size={24} />}
                color="primary"
              />
              <MetricCard
                label="Mediane"
                value={statistics.mediane.toFixed(1)}
                icon={<TrendingUp size={24} />}
                color="default"
              />
              <MetricCard
                label="Taux de reussite"
                value={`${statistics.taux_reussite.toFixed(0)}%`}
                icon={<Users size={24} />}
                color="success"
              />
              <MetricCard
                label="Ecart-type"
                value={statistics.ecart_type.toFixed(2)}
                icon={<BarChart2 size={24} />}
                color="warning"
              />
            </div>
          )}

          {/* Results Table */}
          <Card>
            <CardHeader>
              <CardTitle>Resultats individuels</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoadingResults ? (
                <LoadingSpinner text="Chargement des resultats..." />
              ) : results.length === 0 ? (
                <div className="text-center py-8">
                  <BarChart2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Aucun resultat disponible</p>
                  <p className="text-sm text-gray-400 mt-1">
                    Lancez la correction pour generer les resultats
                  </p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                          Etudiant
                        </th>
                        <th className="text-center py-3 px-4 text-sm font-medium text-gray-500">
                          Note
                        </th>
                        <th className="text-center py-3 px-4 text-sm font-medium text-gray-500">
                          %
                        </th>
                        <th className="text-center py-3 px-4 text-sm font-medium text-gray-500">
                          Performance
                        </th>
                        <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.map((result) => (
                        <tr
                          key={result.id}
                          className="border-b border-gray-100 hover:bg-gray-50"
                        >
                          <td className="py-3 px-4">
                            <p className="font-medium text-gray-900">
                              {result.etudiant_prenom} {result.etudiant_nom}
                            </p>
                          </td>
                          <td className="py-3 px-4 text-center">
                            <span className="font-semibold">
                              {result.note_globale}/{result.note_max}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-center">
                            {result.pourcentage.toFixed(0)}%
                          </td>
                          <td className="py-3 px-4 text-center">
                            <span
                              className={`px-2 py-1 rounded text-xs font-medium ${
                                result.performance === 'excellent'
                                  ? 'bg-green-100 text-green-700'
                                  : result.performance === 'bon'
                                  ? 'bg-blue-100 text-blue-700'
                                  : result.performance === 'moyen'
                                  ? 'bg-yellow-100 text-yellow-700'
                                  : 'bg-red-100 text-red-700'
                              }`}
                            >
                              {result.performance}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right">
                            <Button variant="ghost" size="sm">
                              Details
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
