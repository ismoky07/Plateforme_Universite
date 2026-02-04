export type CorrectionProfile = 'excellence' | 'equilibre' | 'rapide'

export interface QuestionCorrection {
  question_id: string
  numero_question: number
  note_obtenue: number
  note_max: number
  pourcentage: number
  commentaire_intelligent: string
  conseil_personnalise: string
  erreurs_identifiees: string[]
  points_forts: string[]
  points_amelioration: string[]
}

export interface CorrectionResult {
  id: string
  evaluation_id: string
  submission_id: string
  etudiant_nom: string
  etudiant_prenom: string
  note_globale: number
  note_max: number
  pourcentage: number
  rang?: number
  performance: string
  notes_par_question: QuestionCorrection[]
  notes_par_critere: Record<string, number>
  commentaires_generaux: string[]
  suggestions_globales: string[]
  points_forts: string[]
  points_amelioration: string[]
  conseils_revision: string[]
  date_correction: string
  statut_publication: string
}

export interface ClassStatistics {
  evaluation_id: string
  nombre_copies: number
  nombre_corriges: number
  moyenne_generale: number
  mediane: number
  ecart_type: number
  note_min: number
  note_max: number
  taux_reussite: number
  distribution_notes: Record<string, number>
  date_calcul: string
}

export interface CorrectionRequest {
  evaluation_id: string
  profile: CorrectionProfile
  copies_to_correct?: string[]
}

export interface CorrectionProgress {
  evaluation_id: string
  total_copies: number
  copies_traitees: number
  copies_reussies: number
  copies_en_erreur: number
  pourcentage_progression: number
  statut: string
  temps_ecoule_ms: number
}
