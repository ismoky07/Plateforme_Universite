import apiClient, { uploadFormData } from './client'
import {
  Candidature,
  CandidatureSummary,
  CandidatureValidationRequest,
  Grade,
  ValidationStatus,
} from '../types/candidature'

export const candidaturesApi = {
  // List candidatures (admin)
  list: async (params?: {
    statut?: ValidationStatus
    skip?: number
    limit?: number
  }): Promise<Candidature[]> => {
    const response = await apiClient.get<Candidature[]>('/candidatures', { params })
    return response.data
  },

  // Get candidature details
  get: async (candidatureId: string): Promise<Candidature> => {
    const response = await apiClient.get<Candidature>(`/candidatures/${candidatureId}`)
    return response.data
  },

  // Create candidature (public)
  create: async (data: {
    nom: string
    prenom: string
    email: string
    niveau_etude: string
    telephone?: string
    grades: Grade[]
    files?: File[]
  }): Promise<Candidature> => {
    const formData = new FormData()
    formData.append('nom', data.nom)
    formData.append('prenom', data.prenom)
    formData.append('email', data.email)
    formData.append('niveau_etude', data.niveau_etude)

    if (data.telephone) {
      formData.append('telephone', data.telephone)
    }

    formData.append('grades_json', JSON.stringify(data.grades))

    if (data.files) {
      data.files.forEach((file) => {
        formData.append('files', file)
      })
    }

    const response = await uploadFormData('/candidatures', formData)
    return response.data
  },

  // Validate candidature (admin)
  validate: async (
    candidatureId: string,
    request: CandidatureValidationRequest
  ): Promise<{ message: string }> => {
    const response = await apiClient.post(`/candidatures/${candidatureId}/validate`, request)
    return response.data
  },

  // Launch verification (admin)
  verify: async (candidatureId: string): Promise<{ message: string; statut: string }> => {
    const response = await apiClient.post(`/candidatures/${candidatureId}/verify`)
    return response.data
  },

  // Update grades (admin)
  updateGrades: async (candidatureId: string, grades: Grade[]): Promise<Candidature> => {
    const response = await apiClient.put<Candidature>(`/candidatures/${candidatureId}/grades`, grades)
    return response.data
  },

  // Delete candidature
  delete: async (candidatureId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/candidatures/${candidatureId}`)
    return response.data
  },
}
