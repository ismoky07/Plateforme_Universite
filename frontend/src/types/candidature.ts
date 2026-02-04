export type ValidationStatus = 'en_attente' | 'validee' | 'rejetee' | 'en_cours_verification'

export interface PersonalInfo {
  nom: string
  prenom: string
  email: string
  telephone?: string
  niveau_etude: string
  date_naissance?: string
  nationalite?: string
  adresse?: string
}

export interface Grade {
  id?: number
  matiere: string
  note: number
  coefficient: number
  periode: string
  annee: string
}

export interface UploadedDocument {
  year: string
  filename: string
  original_filename: string
  size: number
  file_type: string
  upload_date: string
}

export interface Candidature {
  id: string
  personal_info: PersonalInfo
  grades: Grade[]
  documents: UploadedDocument[]
  date_soumission: string
  statut: ValidationStatus
  dossier_path: string
  moyenne_generale?: number
  completion_percentage: number
  commentaires_admin?: { date: string; auteur: string; commentaire: string }[]
  date_validation?: string
  valide_par?: string
}

export interface CandidatureSummary {
  id: string
  nom: string
  prenom: string
  email: string
  niveau_etude: string
  date_soumission: string
  statut: ValidationStatus
  moyenne_generale?: number
  completion_percentage: number
  nombre_documents: number
}

export interface CandidatureValidationRequest {
  decision: ValidationStatus
  commentaire?: string
  notify_candidate: boolean
}
