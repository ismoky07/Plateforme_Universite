import apiClient from './client'

export interface ReportInfo {
  filename: string
  type: string
  size: number
  created: string
}

export interface StudentReport {
  evaluation_id: string
  evaluation_titre: string
  matiere: string
  note: number
  note_max: number
  date_correction: string
  has_pdf: boolean
}

export const reportsApi = {
  // List reports for evaluation
  listByEvaluation: async (evalId: string): Promise<ReportInfo[]> => {
    const response = await apiClient.get<ReportInfo[]>(`/reports/evaluation/${evalId}`)
    return response.data
  },

  // Get student report
  getStudentReport: async (evalId: string, studentName: string): Promise<Blob> => {
    const response = await apiClient.get(`/reports/evaluation/${evalId}/student/${studentName}`, {
      responseType: 'blob',
    })
    return response.data
  },

  // Generate reports
  generate: async (
    evalId: string,
    format: 'pdf' | 'xlsx' | 'json' = 'pdf'
  ): Promise<{ message: string }> => {
    const response = await apiClient.post(`/reports/evaluation/${evalId}/generate`, null, {
      params: { format },
    })
    return response.data
  },

  // Export results
  exportResults: async (evalId: string, format: 'xlsx' | 'csv' | 'json' = 'xlsx') => {
    const response = await apiClient.get(`/reports/evaluation/${evalId}/export`, {
      params: { format },
    })
    return response.data
  },

  // Get my reports (student)
  getMyReports: async (): Promise<StudentReport[]> => {
    const response = await apiClient.get<StudentReport[]>('/reports/student/my-reports')
    return response.data
  },
}
