import { clsx } from 'clsx'

interface MetricCardProps {
  label: string
  value: string | number
  icon?: React.ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  color?: 'default' | 'primary' | 'success' | 'warning' | 'error'
  className?: string
}

export default function MetricCard({
  label,
  value,
  icon,
  trend,
  color = 'default',
  className,
}: MetricCardProps) {
  const colorStyles = {
    default: 'bg-gray-50 text-gray-600',
    primary: 'bg-primary-50 text-primary-600',
    success: 'bg-green-50 text-green-600',
    warning: 'bg-yellow-50 text-yellow-600',
    error: 'bg-red-50 text-red-600',
  }

  return (
    <div
      className={clsx(
        'bg-white rounded-xl shadow-sm border border-gray-200 p-6',
        className
      )}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{label}</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">{value}</p>

          {trend && (
            <p
              className={clsx(
                'mt-1 text-sm',
                trend.isPositive ? 'text-green-600' : 'text-red-600'
              )}
            >
              {trend.isPositive ? '+' : ''}
              {trend.value}%
            </p>
          )}
        </div>

        {icon && (
          <div className={clsx('p-3 rounded-lg', colorStyles[color])}>
            {icon}
          </div>
        )}
      </div>
    </div>
  )
}
