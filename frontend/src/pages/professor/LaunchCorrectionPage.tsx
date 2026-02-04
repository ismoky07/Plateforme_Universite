import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { evaluationsApi } from '../../api/evaluations'
import { correctionsApi } from '../../api/corrections'
import { useToast } from '../../store/uiStore'
import Card, { CardHeader, CardTitle, CardContent } from '../../components/common/Card'
import Button from '../../components/common/Button'
import Select from '../../components/common/Form/Select'
import AlertBox from '../../components/common/AlertBox'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { Evaluation } from '../../types/evaluation'
import { CorrectionProfile, CorrectionProgress } from '../../types/correction'
import { Play, Zap, Scale, Gauge, CheckCircle } from 'lucide-react'

export default function LaunchCorrectionPage() {
  const [searchParams] = useSearchParams()
  const toast = useToast()

  const [evaluations, setEvaluations] = useState<Evaluation[]>([])
  const [selectedEval, setSelectedEval] = useState<string>(searchParams.get('eval') || '')
  const [profile, setProfile] = useState<CorrectionProfile>('equilibre')
  const [isLoading, setIsLoading] = useState(true)
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState<CorrectionProgress | null>(null)

  useEffect(() => {
    loadEvaluations()
  }, [])

  const loadEvaluations = async () => {
    try {
      const data = await evaluationsApi.list()
      // Filter to only closed evaluations with copies
      const correctable = data.filter(
        (e) => e.statut === 'ferme' && e.nombre_copies > 0
      )
      setEvaluations(correctable)
    } catch (error) {
      console.error('Error loading evaluations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleLaunchCorrection = async () => {
    if (!selectedEval) {
      toast.error('Selectionnez une evaluation')
      return
    }

    setIsProcessing(true)
    setProgress(null)

    try {
      const result = await correctionsApi.process({
        evaluation_id: selectedEval,
        profile,
      })
      setProgress(result)
      toast.success('Correction lancee!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erreur lors du lancement')
    } finally {
      setIsProcessing(false)
    }
  }

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Chargement..." />
  }

  const selectedEvaluation = evaluations.find((e) => e.id === selectedEval)

  const profiles = [
    {
      value: 'excellence',
      label: 'Excellence',
      description: 'GPT-4 - Correction tres detaillee, plus lente',
      icon: <Zap size={24} className="text-yellow-500" />,
    },
    {
      value: 'equilibre',
      label: 'Equilibre (Recommande)',
      description: 'GPT-4o - Bon equilibre qualite/vitesse',
      icon: <Scale size={24} className="text-blue-500" />,
    },
    {
      value: 'rapide',
      label: 'Rapide',
      description: 'GPT-4o-mini - Correction rapide, moins detaillee',
      icon: <Gauge size={24} className="text-green-500" />,
    },
  ]

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Lancer la correction IA</h1>
        <p className="text-gray-600 mt-1">
          Correction automatisee des copies avec intelligence artificielle
        </p>
      </div>

      {evaluations.length === 0 ? (
        <AlertBox
          type="info"
          title="Aucune evaluation disponible"
          message="Il n'y a pas d'evaluation fermee avec des copies a corriger. Fermez une evaluation pour pouvoir lancer la correction."
        />
      ) : (
        <>
          {/* Evaluation Selection */}
          <Card>
            <CardHeader>
              <CardTitle>1. Selectionnez l'evaluation</CardTitle>
            </CardHeader>
            <CardContent>
              <Select
                value={selectedEval}
                onChange={(e) => setSelectedEval(e.target.value)}
                options={evaluations.map((e) => ({
                  value: e.id,
                  label: `${e.titre} - ${e.matiere} (${e.nombre_copies} copies)`,
                }))}
                placeholder="Choisir une evaluation..."
              />

              {selectedEvaluation && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Matiere:</span>{' '}
                      <span className="font-medium">{selectedEvaluation.matiere}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Classe:</span>{' '}
                      <span className="font-medium">{selectedEvaluation.classe}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Copies a corriger:</span>{' '}
                      <span className="font-medium">{selectedEvaluation.nombre_copies}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Deja corrigees:</span>{' '}
                      <span className="font-medium">{selectedEvaluation.nombre_corriges}</span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Profile Selection */}
          <Card>
            <CardHeader>
              <CardTitle>2. Choisissez le profil de correction</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {profiles.map((p) => (
                  <button
                    key={p.value}
                    type="button"
                    onClick={() => setProfile(p.value as CorrectionProfile)}
                    className={`w-full p-4 border-2 rounded-lg text-left transition-colors flex items-center gap-4 ${
                      profile === p.value
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {p.icon}
                    <div>
                      <p className="font-medium text-gray-900">{p.label}</p>
                      <p className="text-sm text-gray-500">{p.description}</p>
                    </div>
                    {profile === p.value && (
                      <CheckCircle className="ml-auto text-primary-500" size={20} />
                    )}
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Progress */}
          {progress && (
            <Card>
              <CardHeader>
                <CardTitle>Progression</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between text-sm">
                    <span>
                      {progress.copies_traitees} / {progress.total_copies} copies
                    </span>
                    <span>{progress.pourcentage_progression.toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-primary-600 h-3 rounded-full transition-all"
                      style={{ width: `${progress.pourcentage_progression}%` }}
                    />
                  </div>
                  <p className="text-sm text-gray-500">
                    Statut: {progress.statut}
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Launch Button */}
          <div className="flex justify-end">
            <Button
              onClick={handleLaunchCorrection}
              isLoading={isProcessing}
              disabled={!selectedEval}
              leftIcon={<Play size={18} />}
              size="lg"
            >
              Lancer la correction
            </Button>
          </div>
        </>
      )}
    </div>
  )
}
