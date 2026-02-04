import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { evaluationsApi } from '../../api/evaluations'
import { submissionsApi } from '../../api/submissions'
import { useToast } from '../../store/uiStore'
import Card, { CardHeader, CardTitle, CardContent } from '../../components/common/Card'
import Button from '../../components/common/Button'
import Input from '../../components/common/Form/Input'
import Select from '../../components/common/Form/Select'
import AlertBox from '../../components/common/AlertBox'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { Evaluation } from '../../types/evaluation'
import { SubmissionType } from '../../types/submission'
import { Upload, FileText, Camera, Edit3 } from 'lucide-react'

export default function SubmitCopyPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const toast = useToast()

  const [evaluations, setEvaluations] = useState<Evaluation[]>([])
  const [selectedEval, setSelectedEval] = useState<string>(searchParams.get('eval') || '')
  const [submissionType, setSubmissionType] = useState<SubmissionType>('fichier_scanne')
  const [files, setFiles] = useState<File[]>([])
  const [digitalResponse, setDigitalResponse] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [hasExistingSubmission, setHasExistingSubmission] = useState(false)

  useEffect(() => {
    loadEvaluations()
  }, [])

  useEffect(() => {
    if (selectedEval && user?.nom && user?.prenom) {
      checkExistingSubmission()
    }
  }, [selectedEval, user])

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

  const checkExistingSubmission = async () => {
    if (!user?.nom || !user?.prenom) return

    try {
      const check = await submissionsApi.checkSubmission(
        selectedEval,
        user.nom,
        user.prenom
      )
      setHasExistingSubmission(check.has_submitted)
    } catch {
      setHasExistingSubmission(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedEval) {
      toast.error('Veuillez selectionner un examen')
      return
    }

    if (!user?.nom || !user?.prenom) {
      toast.error('Informations utilisateur manquantes')
      return
    }

    if (submissionType !== 'numerique' && files.length === 0) {
      toast.error('Veuillez ajouter au moins un fichier')
      return
    }

    if (submissionType === 'numerique' && !digitalResponse.trim()) {
      toast.error('Veuillez saisir votre reponse')
      return
    }

    setIsSubmitting(true)

    try {
      await submissionsApi.create({
        evaluation_id: selectedEval,
        nom: user.nom,
        prenom: user.prenom,
        numero_etudiant: user.numero_etudiant,
        type_soumission: submissionType,
        reponse_numerique: submissionType === 'numerique' ? digitalResponse : undefined,
        files: submissionType !== 'numerique' ? files : undefined,
      })

      toast.success('Copie soumise avec succes!')
      navigate('/student/submissions')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la soumission')
    } finally {
      setIsSubmitting(false)
    }
  }

  const selectedEvaluation = evaluations.find((e) => e.id === selectedEval)

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Chargement..." />
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Soumettre une copie</h1>
        <p className="text-gray-600 mt-1">
          Selectionnez un examen et soumettez votre copie
        </p>
      </div>

      {hasExistingSubmission && (
        <AlertBox
          type="warning"
          title="Soumission existante"
          message="Vous avez deja soumis une copie pour cet examen. Une nouvelle soumission remplacera la precedente."
        />
      )}

      <form onSubmit={handleSubmit}>
        {/* Evaluation Selection */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>1. Selectionnez l'examen</CardTitle>
          </CardHeader>
          <CardContent>
            <Select
              label="Examen"
              value={selectedEval}
              onChange={(e) => setSelectedEval(e.target.value)}
              options={evaluations.map((e) => ({
                value: e.id,
                label: `${e.titre} - ${e.matiere} (${e.classe})`,
              }))}
              placeholder="Choisir un examen..."
            />

            {selectedEvaluation && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Matiere:</span>{' '}
                    <span className="font-medium">{selectedEvaluation.matiere}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Duree:</span>{' '}
                    <span className="font-medium">{selectedEvaluation.duree_minutes} min</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Note max:</span>{' '}
                    <span className="font-medium">{selectedEvaluation.note_totale} pts</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Professeur:</span>{' '}
                    <span className="font-medium">{selectedEvaluation.enseignant || '-'}</span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Submission Type */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>2. Type de soumission</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                type="button"
                onClick={() => setSubmissionType('fichier_scanne')}
                className={`p-4 border-2 rounded-lg text-center transition-colors ${
                  submissionType === 'fichier_scanne'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <FileText className="w-8 h-8 mx-auto mb-2 text-primary-600" />
                <p className="font-medium">PDF scanne</p>
                <p className="text-xs text-gray-500 mt-1">Documents scannes</p>
              </button>

              <button
                type="button"
                onClick={() => setSubmissionType('photo')}
                className={`p-4 border-2 rounded-lg text-center transition-colors ${
                  submissionType === 'photo'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Camera className="w-8 h-8 mx-auto mb-2 text-primary-600" />
                <p className="font-medium">Photos</p>
                <p className="text-xs text-gray-500 mt-1">Images de votre copie</p>
              </button>

              <button
                type="button"
                onClick={() => setSubmissionType('numerique')}
                className={`p-4 border-2 rounded-lg text-center transition-colors ${
                  submissionType === 'numerique'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Edit3 className="w-8 h-8 mx-auto mb-2 text-primary-600" />
                <p className="font-medium">Numerique</p>
                <p className="text-xs text-gray-500 mt-1">Saisie directe</p>
              </button>
            </div>
          </CardContent>
        </Card>

        {/* File Upload or Text Input */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>3. Votre copie</CardTitle>
          </CardHeader>
          <CardContent>
            {submissionType !== 'numerique' ? (
              <div>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-2">
                    Glissez vos fichiers ici ou cliquez pour selectionner
                  </p>
                  <input
                    type="file"
                    multiple
                    accept={submissionType === 'fichier_scanne' ? '.pdf' : 'image/*'}
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload">
                    <Button type="button" variant="secondary" as="span">
                      Parcourir
                    </Button>
                  </label>
                </div>

                {files.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <p className="text-sm font-medium text-gray-700">
                      Fichiers selectionnes ({files.length}):
                    </p>
                    {files.map((file, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-2 bg-gray-50 rounded"
                      >
                        <span className="text-sm">{file.name}</span>
                        <span className="text-xs text-gray-500">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div>
                <textarea
                  value={digitalResponse}
                  onChange={(e) => setDigitalResponse(e.target.value)}
                  placeholder="Saisissez votre reponse ici..."
                  className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <p className="text-sm text-gray-500 mt-2">
                  {digitalResponse.split(/\s+/).filter(Boolean).length} mots |{' '}
                  {digitalResponse.length} caracteres
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Submit Button */}
        <div className="flex justify-end gap-4">
          <Button type="button" variant="secondary" onClick={() => navigate(-1)}>
            Annuler
          </Button>
          <Button type="submit" isLoading={isSubmitting}>
            Soumettre ma copie
          </Button>
        </div>
      </form>
    </div>
  )
}
