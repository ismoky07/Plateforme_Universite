export type SubmissionType = 'fichier_scanne' | 'photo' | 'numerique'
export type SubmissionStatus = 'en_attente' | 'recu' | 'en_traitement' | 'corrige' | 'erreur'

export interface SubmittedFile {
  nom_original: string
  nom_sauvegarde: string
  taille: number
  type_fichier: string
  date_upload: string
}

export interface Submission {
  id: string
  evaluation_id: string
  etudiant_nom: string
  etudiant_prenom: string
  numero_etudiant?: string
  type_soumission: SubmissionType
  date_soumission: string
  statut: SubmissionStatus
  fichiers_soumis: SubmittedFile[]
  nombre_fichiers: number
  taille_totale: number
  reponse_numerique?: boolean
  note_finale?: number
  corrige: boolean
  date_correction?: string
}

export interface SubmissionCreate {
  evaluation_id: string
  nom: string
  prenom: string
  numero_etudiant?: string
  type_soumission: SubmissionType
  reponse_numerique?: string
  files?: File[]
}

export interface StudentSubmissionCheck {
  has_submitted: boolean
  submission_id?: string
  date_soumission?: string
  can_modify: boolean
}
