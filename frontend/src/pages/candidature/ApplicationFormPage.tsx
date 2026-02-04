import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { candidaturesApi } from '../../api/candidatures'
import { useToast } from '../../store/uiStore'
import Card, { CardHeader, CardTitle, CardContent } from '../../components/common/Card'
import Button from '../../components/common/Button'
import Input from '../../components/common/Form/Input'
import Select from '../../components/common/Form/Select'
import { Grade } from '../../types/candidature'
import {
  User,
  BookOpen,
  Upload,
  Send,
  Plus,
  Trash2,
  GraduationCap,
} from 'lucide-react'

type Step = 'personal' | 'grades' | 'documents' | 'review'

export default function ApplicationFormPage() {
  const navigate = useNavigate()
  const toast = useToast()

  const [currentStep, setCurrentStep] = useState<Step>('personal')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Personal info
  const [nom, setNom] = useState('')
  const [prenom, setPrenom] = useState('')
  const [email, setEmail] = useState('')
  const [telephone, setTelephone] = useState('')
  const [niveauEtude, setNiveauEtude] = useState('')

  // Grades
  const [grades, setGrades] = useState<Grade[]>([
    { matiere: '', note: 0, coefficient: 1, periode: '', annee: '' },
  ])

  // Documents
  const [files, setFiles] = useState<File[]>([])

  const steps: { key: Step; label: string; icon: React.ReactNode }[] = [
    { key: 'personal', label: 'Informations', icon: <User size={20} /> },
    { key: 'grades', label: 'Notes', icon: <BookOpen size={20} /> },
    { key: 'documents', label: 'Documents', icon: <Upload size={20} /> },
    { key: 'review', label: 'Validation', icon: <Send size={20} /> },
  ]

  const addGrade = () => {
    setGrades([
      ...grades,
      { matiere: '', note: 0, coefficient: 1, periode: '', annee: '' },
    ])
  }

  const removeGrade = (index: number) => {
    if (grades.length > 1) {
      setGrades(grades.filter((_, i) => i !== index))
    }
  }

  const updateGrade = (index: number, field: keyof Grade, value: any) => {
    setGrades(
      grades.map((g, i) => (i === index ? { ...g, [field]: value } : g))
    )
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles([...files, ...Array.from(e.target.files)])
    }
  }

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  const calculateAverage = () => {
    const validGrades = grades.filter((g) => g.note > 0 && g.coefficient > 0)
    if (validGrades.length === 0) return 0
    const total = validGrades.reduce((sum, g) => sum + g.note * g.coefficient, 0)
    const coefSum = validGrades.reduce((sum, g) => sum + g.coefficient, 0)
    return (total / coefSum).toFixed(2)
  }

  const canProceed = () => {
    switch (currentStep) {
      case 'personal':
        return nom && prenom && email && niveauEtude
      case 'grades':
        return grades.some((g) => g.matiere && g.note > 0)
      case 'documents':
        return true // Documents are optional
      case 'review':
        return true
      default:
        return false
    }
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)

    try {
      await candidaturesApi.create({
        nom,
        prenom,
        email,
        niveau_etude: niveauEtude,
        telephone: telephone || undefined,
        grades: grades.filter((g) => g.matiere && g.note > 0),
        files: files.length > 0 ? files : undefined,
      })

      toast.success('Candidature soumise avec succes!')
      navigate('/login')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la soumission')
    } finally {
      setIsSubmitting(false)
    }
  }

  const niveauOptions = [
    { value: 'bac', label: 'Baccalaureat' },
    { value: 'licence1', label: 'Licence 1' },
    { value: 'licence2', label: 'Licence 2' },
    { value: 'licence3', label: 'Licence 3' },
    { value: 'master1', label: 'Master 1' },
    { value: 'master2', label: 'Master 2' },
  ]

  const matiereOptions = [
    { value: 'Mathematiques', label: 'Mathematiques' },
    { value: 'Francais', label: 'Francais' },
    { value: 'Anglais', label: 'Anglais' },
    { value: 'Physique', label: 'Physique' },
    { value: 'Chimie', label: 'Chimie' },
    { value: 'SVT', label: 'SVT' },
    { value: 'Histoire', label: 'Histoire' },
    { value: 'Geographie', label: 'Geographie' },
    { value: 'Philosophie', label: 'Philosophie' },
    { value: 'Informatique', label: 'Informatique' },
  ]

  const periodeOptions = [
    { value: '1er trimestre', label: '1er trimestre' },
    { value: '2eme trimestre', label: '2eme trimestre' },
    { value: '3eme trimestre', label: '3eme trimestre' },
    { value: '1er semestre', label: '1er semestre' },
    { value: '2eme semestre', label: '2eme semestre' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4">
            <GraduationCap className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Depot de candidature</h1>
          <p className="text-gray-600 mt-1">Universite - Annee 2024-2025</p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-between mb-8">
          {steps.map((step, index) => (
            <div key={step.key} className="flex items-center">
              <div
                className={`flex items-center justify-center w-10 h-10 rounded-full ${
                  currentStep === step.key
                    ? 'bg-primary-600 text-white'
                    : steps.findIndex((s) => s.key === currentStep) > index
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 text-gray-500'
                }`}
              >
                {step.icon}
              </div>
              <span
                className={`ml-2 text-sm font-medium hidden md:block ${
                  currentStep === step.key ? 'text-primary-600' : 'text-gray-500'
                }`}
              >
                {step.label}
              </span>
              {index < steps.length - 1 && (
                <div className="w-12 md:w-24 h-1 mx-2 bg-gray-200 rounded">
                  <div
                    className={`h-full rounded ${
                      steps.findIndex((s) => s.key === currentStep) > index
                        ? 'bg-green-500'
                        : ''
                    }`}
                  />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Form Content */}
        <Card>
          <CardContent>
            {/* Step 1: Personal Info */}
            {currentStep === 'personal' && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold mb-4">Informations personnelles</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Nom *"
                    value={nom}
                    onChange={(e) => setNom(e.target.value)}
                    placeholder="Votre nom de famille"
                    required
                  />
                  <Input
                    label="Prenom *"
                    value={prenom}
                    onChange={(e) => setPrenom(e.target.value)}
                    placeholder="Votre prenom"
                    required
                  />
                  <Input
                    label="Email *"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="votre@email.com"
                    required
                  />
                  <Input
                    label="Telephone"
                    value={telephone}
                    onChange={(e) => setTelephone(e.target.value)}
                    placeholder="06 12 34 56 78"
                  />
                  <div className="md:col-span-2">
                    <Select
                      label="Niveau d'etude vise *"
                      value={niveauEtude}
                      onChange={(e) => setNiveauEtude(e.target.value)}
                      options={niveauOptions}
                      placeholder="Selectionnez..."
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: Grades */}
            {currentStep === 'grades' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">Notes scolaires</h2>
                  <span className="text-sm text-gray-500">
                    Moyenne: <strong>{calculateAverage()}/20</strong>
                  </span>
                </div>

                {grades.map((grade, index) => (
                  <div
                    key={index}
                    className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                      <Select
                        label="Matiere"
                        value={grade.matiere}
                        onChange={(e) => updateGrade(index, 'matiere', e.target.value)}
                        options={matiereOptions}
                        placeholder="Matiere..."
                      />
                      <Input
                        label="Note /20"
                        type="number"
                        value={grade.note}
                        onChange={(e) =>
                          updateGrade(index, 'note', parseFloat(e.target.value))
                        }
                        min={0}
                        max={20}
                        step={0.5}
                      />
                      <Input
                        label="Coefficient"
                        type="number"
                        value={grade.coefficient}
                        onChange={(e) =>
                          updateGrade(index, 'coefficient', parseInt(e.target.value))
                        }
                        min={1}
                        max={10}
                      />
                      <Select
                        label="Periode"
                        value={grade.periode}
                        onChange={(e) => updateGrade(index, 'periode', e.target.value)}
                        options={periodeOptions}
                        placeholder="Periode..."
                      />
                      <div className="flex items-end">
                        <Button
                          type="button"
                          variant="ghost"
                          onClick={() => removeGrade(index)}
                          disabled={grades.length === 1}
                        >
                          <Trash2 size={18} className="text-red-500" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}

                <Button
                  type="button"
                  variant="secondary"
                  onClick={addGrade}
                  leftIcon={<Plus size={18} />}
                >
                  Ajouter une note
                </Button>
              </div>
            )}

            {/* Step 3: Documents */}
            {currentStep === 'documents' && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold mb-4">Documents justificatifs</h2>
                <p className="text-sm text-gray-600 mb-4">
                  Ajoutez vos bulletins scolaires et autres documents (PDF, JPG, PNG)
                </p>

                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-2">
                    Glissez vos fichiers ici ou cliquez pour selectionner
                  </p>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleFileChange}
                    className="hidden"
                    id="doc-upload"
                  />
                  <label htmlFor="doc-upload">
                    <Button type="button" variant="secondary" as="span">
                      Parcourir
                    </Button>
                  </label>
                </div>

                {files.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-gray-700">
                      Documents ajoutes ({files.length}):
                    </p>
                    {files.map((file, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded"
                      >
                        <span className="text-sm">{file.name}</span>
                        <button
                          onClick={() => removeFile(index)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Step 4: Review */}
            {currentStep === 'review' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold mb-4">Recapitulatif</h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-medium text-gray-700 mb-2">Informations</h3>
                    <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                      <p>
                        <span className="text-gray-500">Nom:</span> {prenom} {nom}
                      </p>
                      <p>
                        <span className="text-gray-500">Email:</span> {email}
                      </p>
                      <p>
                        <span className="text-gray-500">Telephone:</span>{' '}
                        {telephone || 'Non renseigne'}
                      </p>
                      <p>
                        <span className="text-gray-500">Niveau:</span> {niveauEtude}
                      </p>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-medium text-gray-700 mb-2">Notes</h3>
                    <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                      <p>
                        <span className="text-gray-500">Nombre de notes:</span>{' '}
                        {grades.filter((g) => g.matiere).length}
                      </p>
                      <p>
                        <span className="text-gray-500">Moyenne:</span>{' '}
                        <strong>{calculateAverage()}/20</strong>
                      </p>
                    </div>
                  </div>

                  <div className="md:col-span-2">
                    <h3 className="font-medium text-gray-700 mb-2">Documents</h3>
                    <div className="bg-gray-50 rounded-lg p-4 text-sm">
                      {files.length > 0 ? (
                        <ul className="list-disc list-inside">
                          {files.map((f, i) => (
                            <li key={i}>{f.name}</li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-500">Aucun document ajoute</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Navigation */}
            <div className="flex justify-between mt-8 pt-6 border-t">
              {currentStep !== 'personal' ? (
                <Button
                  variant="secondary"
                  onClick={() => {
                    const stepIndex = steps.findIndex((s) => s.key === currentStep)
                    setCurrentStep(steps[stepIndex - 1].key)
                  }}
                >
                  Precedent
                </Button>
              ) : (
                <div />
              )}

              {currentStep === 'review' ? (
                <Button
                  onClick={handleSubmit}
                  isLoading={isSubmitting}
                  leftIcon={<Send size={18} />}
                >
                  Soumettre ma candidature
                </Button>
              ) : (
                <Button
                  onClick={() => {
                    const stepIndex = steps.findIndex((s) => s.key === currentStep)
                    setCurrentStep(steps[stepIndex + 1].key)
                  }}
                  disabled={!canProceed()}
                >
                  Suivant
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Back to login */}
        <p className="text-center mt-6 text-gray-600">
          Deja un compte?{' '}
          <a href="/login" className="text-primary-600 hover:underline font-medium">
            Se connecter
          </a>
        </p>
      </div>
    </div>
  )
}
