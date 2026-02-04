import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { evaluationsApi } from '../../api/evaluations'
import { useToast } from '../../store/uiStore'
import Card, { CardHeader, CardTitle, CardContent } from '../../components/common/Card'
import Button from '../../components/common/Button'
import Input from '../../components/common/Form/Input'
import Select from '../../components/common/Form/Select'
import { Question } from '../../types/evaluation'
import { Plus, Trash2, Save } from 'lucide-react'

export default function CreateEvaluationPage() {
  const navigate = useNavigate()
  const toast = useToast()

  const [isSubmitting, setIsSubmitting] = useState(false)

  // Form state
  const [titre, setTitre] = useState('')
  const [matiere, setMatiere] = useState('')
  const [classe, setClasse] = useState('')
  const [typeEpreuve, setTypeEpreuve] = useState('examen')
  const [dureeMinutes, setDureeMinutes] = useState(120)
  const [dateExamen, setDateExamen] = useState('')
  const [heureDebut, setHeureDebut] = useState('')
  const [enseignant, setEnseignant] = useState('')
  const [consignes, setConsignes] = useState('')

  // Questions
  const [questions, setQuestions] = useState<Question[]>([
    { id: '1', numero: 1, texte: '', points: 5, type_question: 'redaction' },
  ])

  const addQuestion = () => {
    const newId = (questions.length + 1).toString()
    setQuestions([
      ...questions,
      {
        id: newId,
        numero: questions.length + 1,
        texte: '',
        points: 5,
        type_question: 'redaction',
      },
    ])
  }

  const removeQuestion = (id: string) => {
    if (questions.length > 1) {
      const updated = questions
        .filter((q) => q.id !== id)
        .map((q, idx) => ({ ...q, numero: idx + 1 }))
      setQuestions(updated)
    }
  }

  const updateQuestion = (id: string, field: keyof Question, value: any) => {
    setQuestions(
      questions.map((q) => (q.id === id ? { ...q, [field]: value } : q))
    )
  }

  const totalPoints = questions.reduce((sum, q) => sum + q.points, 0)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!titre || !matiere || !classe) {
      toast.error('Veuillez remplir tous les champs obligatoires')
      return
    }

    setIsSubmitting(true)

    try {
      await evaluationsApi.create({
        titre,
        matiere,
        classe,
        type_epreuve: typeEpreuve,
        duree_minutes: dureeMinutes,
        date_examen: dateExamen || undefined,
        heure_debut: heureDebut || undefined,
        enseignant: enseignant || undefined,
        questions,
        note_totale: totalPoints,
      })

      toast.success('Evaluation creee avec succes!')
      navigate('/professor')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la creation')
    } finally {
      setIsSubmitting(false)
    }
  }

  const matiereOptions = [
    { value: 'Mathematiques', label: 'Mathematiques' },
    { value: 'Francais', label: 'Francais' },
    { value: 'Physique', label: 'Physique' },
    { value: 'Chimie', label: 'Chimie' },
    { value: 'SVT', label: 'SVT' },
    { value: 'Histoire', label: 'Histoire' },
    { value: 'Geographie', label: 'Geographie' },
    { value: 'Anglais', label: 'Anglais' },
    { value: 'Philosophie', label: 'Philosophie' },
    { value: 'Informatique', label: 'Informatique' },
  ]

  const classeOptions = [
    { value: '6eme', label: '6eme' },
    { value: '5eme', label: '5eme' },
    { value: '4eme', label: '4eme' },
    { value: '3eme', label: '3eme' },
    { value: '2nde', label: '2nde' },
    { value: '1ere', label: '1ere' },
    { value: 'Terminale', label: 'Terminale' },
    { value: 'L1', label: 'Licence 1' },
    { value: 'L2', label: 'Licence 2' },
    { value: 'L3', label: 'Licence 3' },
  ]

  const typeOptions = [
    { value: 'examen', label: 'Examen' },
    { value: 'controle', label: 'Controle' },
    { value: 'devoir', label: 'Devoir maison' },
    { value: 'tp', label: 'TP' },
  ]

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Creer une evaluation</h1>
        <p className="text-gray-600 mt-1">
          Configurez votre evaluation et definissez les questions
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Basic Info */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Informations generales</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Titre de l'evaluation *"
                value={titre}
                onChange={(e) => setTitre(e.target.value)}
                placeholder="Ex: Examen final - Chapitre 5"
                required
              />
              <Input
                label="Professeur"
                value={enseignant}
                onChange={(e) => setEnseignant(e.target.value)}
                placeholder="Votre nom"
              />
              <Select
                label="Matiere *"
                value={matiere}
                onChange={(e) => setMatiere(e.target.value)}
                options={matiereOptions}
                placeholder="Selectionnez..."
              />
              <Select
                label="Classe *"
                value={classe}
                onChange={(e) => setClasse(e.target.value)}
                options={classeOptions}
                placeholder="Selectionnez..."
              />
              <Select
                label="Type d'epreuve"
                value={typeEpreuve}
                onChange={(e) => setTypeEpreuve(e.target.value)}
                options={typeOptions}
              />
              <Input
                label="Duree (minutes)"
                type="number"
                value={dureeMinutes}
                onChange={(e) => setDureeMinutes(parseInt(e.target.value))}
                min={15}
                max={480}
              />
              <Input
                label="Date"
                type="date"
                value={dateExamen}
                onChange={(e) => setDateExamen(e.target.value)}
              />
              <Input
                label="Heure de debut"
                type="time"
                value={heureDebut}
                onChange={(e) => setHeureDebut(e.target.value)}
              />
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Consignes specifiques
              </label>
              <textarea
                value={consignes}
                onChange={(e) => setConsignes(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows={3}
                placeholder="Instructions particulieres pour les etudiants..."
              />
            </div>
          </CardContent>
        </Card>

        {/* Questions */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Questions ({questions.length})</CardTitle>
              <div className="text-sm text-gray-500">
                Total: <span className="font-semibold">{totalPoints} points</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {questions.map((question) => (
                <div
                  key={question.id}
                  className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-primary-600">
                        {question.numero}
                      </span>
                    </div>
                    <div className="flex-1 space-y-3">
                      <Input
                        placeholder="Enonce de la question..."
                        value={question.texte}
                        onChange={(e) =>
                          updateQuestion(question.id, 'texte', e.target.value)
                        }
                      />
                      <div className="flex gap-4">
                        <div className="w-32">
                          <Input
                            label="Points"
                            type="number"
                            value={question.points}
                            onChange={(e) =>
                              updateQuestion(
                                question.id,
                                'points',
                                parseFloat(e.target.value)
                              )
                            }
                            min={0.5}
                            step={0.5}
                          />
                        </div>
                        <div className="w-48">
                          <Select
                            label="Type"
                            value={question.type_question}
                            onChange={(e) =>
                              updateQuestion(question.id, 'type_question', e.target.value)
                            }
                            options={[
                              { value: 'redaction', label: 'Redaction' },
                              { value: 'qcm', label: 'QCM' },
                              { value: 'calcul', label: 'Calcul' },
                              { value: 'exercice', label: 'Exercice' },
                            ]}
                          />
                        </div>
                      </div>
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeQuestion(question.id)}
                      disabled={questions.length === 1}
                    >
                      <Trash2 size={18} className="text-red-500" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            <Button
              type="button"
              variant="secondary"
              className="mt-4"
              leftIcon={<Plus size={18} />}
              onClick={addQuestion}
            >
              Ajouter une question
            </Button>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <Button type="button" variant="secondary" onClick={() => navigate(-1)}>
            Annuler
          </Button>
          <Button type="submit" isLoading={isSubmitting} leftIcon={<Save size={18} />}>
            Creer l'evaluation
          </Button>
        </div>
      </form>
    </div>
  )
}
