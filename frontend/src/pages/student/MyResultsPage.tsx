import { useEffect, useState } from 'react'
import { reportsApi, StudentReport } from '../../api/reports'
import Card, { CardHeader, CardTitle, CardContent } from '../../components/common/Card'
import MetricCard from '../../components/common/MetricCard'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import Button from '../../components/common/Button'
import { BarChart2, Award, TrendingUp, Download, FileText } from 'lucide-react'

export default function MyResultsPage() {
  const [reports, setReports] = useState<StudentReport[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadReports()
  }, [])

  const loadReports = async () => {
    try {
      const data = await reportsApi.getMyReports()
      setReports(data)
    } catch (error) {
      console.error('Error loading reports:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownloadReport = async (evalId: string, studentName: string) => {
    try {
      const blob = await reportsApi.getStudentReport(evalId, studentName)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `rapport_${evalId}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading report:', error)
    }
  }

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Chargement des resultats..." />
  }

  const avgNote = reports.length > 0
    ? reports.reduce((sum, r) => sum + (r.note / r.note_max) * 20, 0) / reports.length
    : 0

  const bestNote = reports.length > 0
    ? Math.max(...reports.map((r) => (r.note / r.note_max) * 20))
    : 0

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Mes resultats</h1>
        <p className="text-gray-600 mt-1">
          Consultez vos notes et telechargez vos rapports
        </p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          label="Evaluations"
          value={reports.length}
          icon={<FileText size={24} />}
          color="primary"
        />
        <MetricCard
          label="Moyenne generale"
          value={avgNote.toFixed(1)}
          icon={<BarChart2 size={24} />}
          color="default"
        />
        <MetricCard
          label="Meilleure note"
          value={bestNote.toFixed(1)}
          icon={<Award size={24} />}
          color="success"
        />
        <MetricCard
          label="Progression"
          value="+2.3"
          icon={<TrendingUp size={24} />}
          color="success"
        />
      </div>

      {/* Results List */}
      {reports.length === 0 ? (
        <Card className="text-center py-12">
          <BarChart2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900">Aucun resultat</h3>
          <p className="text-gray-500 mt-1">
            Vos resultats apparaitront ici une fois publies
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {reports.map((report) => {
            const percentage = (report.note / report.note_max) * 100
            const performance =
              percentage >= 80
                ? 'Excellent'
                : percentage >= 60
                ? 'Bien'
                : percentage >= 40
                ? 'Passable'
                : 'Insuffisant'

            return (
              <Card key={report.evaluation_id}>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {report.evaluation_titre}
                    </h3>
                    <p className="text-sm text-gray-500 mb-3">{report.matiere}</p>

                    {/* Progress bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        className={`h-2.5 rounded-full ${
                          percentage >= 60
                            ? 'bg-green-500'
                            : percentage >= 40
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-gray-900">
                        {report.note}
                      </p>
                      <p className="text-sm text-gray-500">/ {report.note_max}</p>
                    </div>

                    <div className="text-center">
                      <p className="text-lg font-semibold text-gray-900">
                        {percentage.toFixed(0)}%
                      </p>
                      <p
                        className={`text-sm ${
                          percentage >= 60
                            ? 'text-green-600'
                            : percentage >= 40
                            ? 'text-yellow-600'
                            : 'text-red-600'
                        }`}
                      >
                        {performance}
                      </p>
                    </div>

                    {report.has_pdf && (
                      <Button
                        variant="secondary"
                        size="sm"
                        leftIcon={<Download size={16} />}
                        onClick={() =>
                          handleDownloadReport(
                            report.evaluation_id,
                            'student_name' // Replace with actual student name
                          )
                        }
                      >
                        PDF
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
