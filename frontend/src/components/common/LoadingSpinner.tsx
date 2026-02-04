import { clsx } from 'clsx'
import { Loader2 } from 'lucide-react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  fullScreen?: boolean
  text?: string
}

export default function LoadingSpinner({
  size = 'md',
  className,
  fullScreen = false,
  text,
}: LoadingSpinnerProps) {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }

  const spinner = (
    <div className={clsx('flex flex-col items-center justify-center', className)}>
      <Loader2 className={clsx(sizes[size], 'animate-spin text-primary-600')} />
      {text && <p className="mt-2 text-sm text-gray-600">{text}</p>}
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50">
        {spinner}
      </div>
    )
  }

  return spinner
}
