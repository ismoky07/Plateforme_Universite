import apiClient from './client'
import { Evaluation, EvaluationCreate } from '../types/evaluation'

export const evaluationsApi = {
  // List all evaluations
  list: async (params?: {
    matiere?: string
    statut?: string
    skip?: number
    limit?: number
  }): Promise<Evaluation[]> => {
    const response = await apiClient.get<Evaluation[]>('/evaluations', { params })
    return response.data
  },

  // List available evaluations (for students)
  listAvailable: async (): Promise<Evaluation[]> => {
    const response = await apiClient.get<Evaluation[]>('/evaluations/available')
    return response.data
  },

  // Get single evaluation
  get: async (evalId: string): Promise<Evaluation> => {
    const response = await apiClient.get<Evaluation>(`/evaluations/${evalId}`)
    return response.data
  },

  // Create evaluation
  create: async (data: EvaluationCreate): Promise<Evaluation> => {
    const response = await apiClient.post<Evaluation>('/evaluations', data)
    return response.data
  },

  // Update evaluation
  update: async (evalId: string, data: Partial<EvaluationCreate>): Promise<Evaluation> => {
    const response = await apiClient.put<Evaluation>(`/evaluations/${evalId}`, data)
    return response.data
  },

  // Open evaluation
  open: async (evalId: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/evaluations/${evalId}/open`)
    return response.data
  },

  // Close evaluation
  close: async (evalId: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/evaluations/${evalId}/close`)
    return response.data
  },

  // Publish results
  publish: async (
    evalId: string,
    options?: { notify_students?: boolean; message?: string }
  ): Promise<{ message: string }> => {
    const response = await apiClient.post(`/evaluations/${evalId}/publish`, options || {})
    return response.data
  },

  // Unpublish results
  unpublish: async (evalId: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/evaluations/${evalId}/unpublish`)
    return response.data
  },

  // Delete evaluation
  delete: async (evalId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/evaluations/${evalId}`)
    return response.data
  },
}
