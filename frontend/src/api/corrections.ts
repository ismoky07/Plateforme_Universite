import apiClient from './client'
import {
  CorrectionResult,
  ClassStatistics,
  CorrectionRequest,
  CorrectionProgress,
} from '../types/correction'

export const correctionsApi = {
  // Launch correction process
  process: async (request: CorrectionRequest): Promise<CorrectionProgress> => {
    const response = await apiClient.post<CorrectionProgress>('/corrections/process', request)
    return response.data
  },

  // Get results for evaluation
  getResults: async (evalId: string): Promise<CorrectionResult[]> => {
    const response = await apiClient.get<CorrectionResult[]>(
      `/corrections/evaluation/${evalId}/results`
    )
    return response.data
  },

  // Get statistics for evaluation
  getStatistics: async (evalId: string): Promise<ClassStatistics> => {
    const response = await apiClient.get<ClassStatistics>(
      `/corrections/evaluation/${evalId}/statistics`
    )
    return response.data
  },

  // Get student result
  getStudentResult: async (
    evalId: string,
    nom: string,
    prenom: string
  ): Promise<CorrectionResult> => {
    const response = await apiClient.get<CorrectionResult>(`/corrections/student/${evalId}`, {
      params: { nom, prenom },
    })
    return response.data
  },

  // Save correction result
  saveResult: async (evalId: string, result: Partial<CorrectionResult>): Promise<{ message: string }> => {
    const response = await apiClient.post(`/corrections/evaluation/${evalId}/result`, result)
    return response.data
  },
}
