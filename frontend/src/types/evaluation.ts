export type EvaluationStatus = 'brouillon' | 'ouvert' | 'ferme' | 'expire'
export type PublicationStatus = 'brouillon' | 'publie' | 'depublie'

export interface Question {
  id: string
  numero: number
  texte: string
  points: number
  type_question: string
  criteres?: Record<string, number>
  reponse_attendue?: string
}

export interface Evaluation {
  id: string
  titre: string
  matiere: string
  classe: string
  type_epreuve: string
  duree_minutes: number
  date_examen?: string
  heure_debut?: string
  enseignant?: string
  etablissement?: string
  consignes_specifiques?: string
  questions: Question[]
  note_totale: number
  statut: EvaluationStatus
  statut_publication: PublicationStatus
  date_creation: string
  date_publication?: string
  dossier: string
  nombre_copies: number
  nombre_corriges: number
}

export interface EvaluationCreate {
  titre: string
  matiere: string
  classe: string
  type_epreuve: string
  duree_minutes: number
  date_examen?: string
  heure_debut?: string
  enseignant?: string
  questions: Question[]
  note_totale: number
}

export interface EvaluationSummary {
  id: string
  titre: string
  matiere: string
  classe: string
  statut: EvaluationStatus
  statut_publication: PublicationStatus
  nombre_copies: number
  date_creation: string
}
