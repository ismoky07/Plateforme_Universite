import { useEffect, useState } from 'react'
import { candidaturesApi } from '../../api/candidatures'
import { useToast } from '../../store/uiStore'
import Card, { CardHeader, CardTitle, CardContent } from '../../components/common/Card'
import MetricCard from '../../components/common/MetricCard'
import Button from '../../components/common/Button'
import Select from '../../components/common/Form/Select'
import StatusBadge from '../../components/common/StatusBadge'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { Candidature, ValidationStatus } from '../../types/candidature'
import {
  ClipboardList,
  CheckCircle,
  XCircle,
  Clock,
  Search,
  Eye,
  RefreshCw,
} from 'lucide-react'

export default function CandidaturesPage() {
  const toast = useToast()

  const [candidatures, setCandidatures] = useState<Candidature[]>([])
  const [filteredCandidatures, setFilteredCandidatures] = useState<Candidature[]>([])
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [selectedCandidature, setSelectedCandidature] = useState<Candidature | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadCandidatures()
  }, [])

  useEffect(() => {
    if (statusFilter === 'all') {
      setFilteredCandidatures(candidatures)
    } else {
      setFilteredCandidatures(candidatures.filter((c) => c.statut === statusFilter))
    }
  }, [statusFilter, candidatures])

  const loadCandidatures = async () => {
    try {
      const data = await candidaturesApi.list()
      setCandidatures(data)
      setFilteredCandidatures(data)
    } catch (error) {
      console.error('Error loading candidatures:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleValidate = async (id: string) => {
    try {
      await candidaturesApi.validate(id, {
        decision: 'validee' as ValidationStatus,
        notify_candidate: true,
      })
      toast.success('Candidature validee!')
      loadCandidatures()
      setSelectedCandidature(null)
    } catch (error) {
      toast.error('Erreur lors de la validation')
    }
  }

  const handleReject = async (id: string) => {
    try {
      await candidaturesApi.validate(id, {
        decision: 'rejetee' as ValidationStatus,
        notify_candidate: true,
      })
      toast.success('Candidature rejetee')
      loadCandidatures()
      setSelectedCandidature(null)
    } catch (error) {
      toast.error('Erreur')
    }
  }

  const handleVerify = async (id: string) => {
    try {
      await candidaturesApi.verify(id)
      toast.info('Verification OCR lancee')
      loadCandidatures()
    } catch (error) {
      toast.error('Erreur lors de la verification')
    }
  }

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Chargement..." />
  }

  const pendingCount = candidatures.filter((c) => c.statut === 'en_attente').length
  const validatedCount = candidatures.filter((c) => c.statut === 'validee').length
  const rejectedCount = candidatures.filter((c) => c.statut === 'rejetee').length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Candidatures</h1>
          <p className="text-gray-600 mt-1">
            Gerez les candidatures des etudiants
          </p>
        </div>
        <Button onClick={loadCandidatures} variant="secondary" leftIcon={<RefreshCw size={18} />}>
          Actualiser
        </Button>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          label="Total"
          value={candidatures.length}
          icon={<ClipboardList size={24} />}
          color="primary"
        />
        <MetricCard
          label="En attente"
          value={pendingCount}
          icon={<Clock size={24} />}
          color="warning"
        />
        <MetricCard
          label="Validees"
          value={validatedCount}
          icon={<CheckCircle size={24} />}
          color="success"
        />
        <MetricCard
          label="Rejetees"
          value={rejectedCount}
          icon={<XCircle size={24} />}
          color="error"
        />
      </div>

      {/* Filter */}
      <Card>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="w-64">
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'Tous les statuts' },
                  { value: 'en_attente', label: 'En attente' },
                  { value: 'validee', label: 'Validees' },
                  { value: 'rejetee', label: 'Rejetees' },
                  { value: 'en_cours_verification', label: 'En verification' },
                ]}
              />
            </div>
            <span className="text-sm text-gray-500">
              {filteredCandidatures.length} candidature(s)
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Candidatures List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* List */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Liste des candidatures</CardTitle>
            </CardHeader>
            <CardContent>
              {filteredCandidatures.length === 0 ? (
                <div className="text-center py-8">
                  <ClipboardList className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Aucune candidature</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredCandidatures.map((cand) => (
                    <div
                      key={cand.id}
                      onClick={() => setSelectedCandidature(cand)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                        selectedCandidature?.id === cand.id
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">
                            {cand.personal_info.prenom} {cand.personal_info.nom}
                          </h4>
                          <p className="text-sm text-gray-500">
                            {cand.personal_info.email}
                          </p>
                          <div className="flex items-center gap-3 mt-2 text-sm text-gray-500">
                            <span>{cand.personal_info.niveau_etude}</span>
                            <span>|</span>
                            <span>{cand.documents.length} document(s)</span>
                            <span>|</span>
                            <span>
                              Moyenne: {cand.moyenne_generale?.toFixed(1) || '-'}/20
                            </span>
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          <StatusBadge status={cand.statut} />
                          <span className="text-xs text-gray-500">
                            {new Date(cand.date_soumission).toLocaleDateString('fr-FR')}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Details Panel */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Details</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedCandidature ? (
                <div className="space-y-4">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900">
                      {selectedCandidature.personal_info.prenom}{' '}
                      {selectedCandidature.personal_info.nom}
                    </h4>
                    <StatusBadge status={selectedCandidature.statut} />
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Email:</span>
                      <span>{selectedCandidature.personal_info.email}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Telephone:</span>
                      <span>{selectedCandidature.personal_info.telephone || '-'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Niveau:</span>
                      <span>{selectedCandidature.personal_info.niveau_etude}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Moyenne:</span>
                      <span className="font-semibold">
                        {selectedCandidature.moyenne_generale?.toFixed(1) || '-'}/20
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Completion:</span>
                      <span>{selectedCandidature.completion_percentage}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Documents:</span>
                      <span>{selectedCandidature.documents.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Notes:</span>
                      <span>{selectedCandidature.grades.length}</span>
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Completion du dossier</span>
                      <span>{selectedCandidature.completion_percentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${selectedCandidature.completion_percentage}%` }}
                      />
                    </div>
                  </div>

                  {/* Actions */}
                  {selectedCandidature.statut === 'en_attente' && (
                    <div className="flex flex-col gap-2 pt-4 border-t">
                      <Button
                        variant="secondary"
                        onClick={() => handleVerify(selectedCandidature.id)}
                        leftIcon={<Search size={16} />}
                      >
                        Lancer verification OCR
                      </Button>
                      <div className="flex gap-2">
                        <Button
                          variant="success"
                          className="flex-1"
                          onClick={() => handleValidate(selectedCandidature.id)}
                          leftIcon={<CheckCircle size={16} />}
                        >
                          Valider
                        </Button>
                        <Button
                          variant="danger"
                          className="flex-1"
                          onClick={() => handleReject(selectedCandidature.id)}
                          leftIcon={<XCircle size={16} />}
                        >
                          Rejeter
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">
                  Selectionnez une candidature pour voir les details
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
