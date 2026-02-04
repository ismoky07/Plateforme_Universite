import { clsx } from 'clsx'
import { AlertCircle, CheckCircle, Info, XCircle, X } from 'lucide-react'

interface AlertBoxProps {
  type: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  onClose?: () => void
  className?: string
}

export default function AlertBox({
  type,
  title,
  message,
  onClose,
  className,
}: AlertBoxProps) {
  const styles = {
    success: {
      bg: 'bg-green-50 border-green-200',
      icon: <CheckCircle className="w-5 h-5 text-green-500" />,
      title: 'text-green-800',
      message: 'text-green-700',
    },
    error: {
      bg: 'bg-red-50 border-red-200',
      icon: <XCircle className="w-5 h-5 text-red-500" />,
      title: 'text-red-800',
      message: 'text-red-700',
    },
    warning: {
      bg: 'bg-yellow-50 border-yellow-200',
      icon: <AlertCircle className="w-5 h-5 text-yellow-500" />,
      title: 'text-yellow-800',
      message: 'text-yellow-700',
    },
    info: {
      bg: 'bg-blue-50 border-blue-200',
      icon: <Info className="w-5 h-5 text-blue-500" />,
      title: 'text-blue-800',
      message: 'text-blue-700',
    },
  }

  const style = styles[type]

  return (
    <div
      className={clsx(
        'rounded-lg border p-4 flex gap-3',
        style.bg,
        className
      )}
    >
      <div className="flex-shrink-0">{style.icon}</div>
      <div className="flex-1">
        {title && (
          <h4 className={clsx('font-medium', style.title)}>{title}</h4>
        )}
        <p className={clsx('text-sm', title && 'mt-1', style.message)}>
          {message}
        </p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 text-gray-400 hover:text-gray-600"
        >
          <X className="w-5 h-5" />
        </button>
      )}
    </div>
  )
}
