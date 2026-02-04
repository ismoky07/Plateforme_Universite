import { uploadFormData } from './client'
import apiClient from './client'
import { Submission, SubmissionCreate, StudentSubmissionCheck } from '../types/submission'

export const submissionsApi = {
  // Create submission
  create: async (data: SubmissionCreate): Promise<Submission> => {
    const formData = new FormData()
    formData.append('evaluation_id', data.evaluation_id)
    formData.append('nom', data.nom)
    formData.append('prenom', data.prenom)
    formData.append('type_soumission', data.type_soumission)

    if (data.numero_etudiant) {
      formData.append('numero_etudiant', data.numero_etudiant)
    }

    if (data.reponse_numerique) {
      formData.append('reponse_numerique', data.reponse_numerique)
    }

    if (data.files) {
      data.files.forEach((file) => {
        formData.append('files', file)
      })
    }

    const response = await uploadFormData('/submissions', formData)
    return response.data
  },

  // List submissions for evaluation
  listByEvaluation: async (evalId: string): Promise<Submission[]> => {
    const response = await apiClient.get<Submission[]>(`/submissions/evaluation/${evalId}`)
    return response.data
  },

  // Check if student submitted
  checkSubmission: async (evalId: string, nom: string, prenom: string): Promise<StudentSubmissionCheck> => {
    const response = await apiClient.get<StudentSubmissionCheck>(`/submissions/check/${evalId}`, {
      params: { nom, prenom },
    })
    return response.data
  },

  // Get submission details
  get: async (submissionId: string, evalId: string): Promise<Submission> => {
    const response = await apiClient.get<Submission>(`/submissions/${submissionId}`, {
      params: { eval_id: evalId },
    })
    return response.data
  },

  // Delete submission
  delete: async (submissionId: string, evalId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/submissions/${submissionId}`, {
      params: { eval_id: evalId },
    })
    return response.data
  },
}
