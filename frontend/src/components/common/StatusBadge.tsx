import { clsx } from 'clsx'

type BadgeVariant = 'success' | 'warning' | 'error' | 'info' | 'default'

interface StatusBadgeProps {
  status: string
  variant?: BadgeVariant
  className?: string
}

// Status to variant mapping
const statusVariants: Record<string, BadgeVariant> = {
  // Evaluation status
  brouillon: 'default',
  ouvert: 'success',
  ferme: 'warning',
  expire: 'error',
  publie: 'success',
  depublie: 'warning',

  // Submission status
  en_attente: 'warning',
  recu: 'info',
  en_traitement: 'info',
  corrige: 'success',
  erreur: 'error',

  // Candidature status
  validee: 'success',
  rejetee: 'error',
  en_cours_verification: 'info',
}

// Status to label mapping
const statusLabels: Record<string, string> = {
  brouillon: 'Brouillon',
  ouvert: 'Ouvert',
  ferme: 'Ferme',
  expire: 'Expire',
  publie: 'Publie',
  depublie: 'Depublie',
  en_attente: 'En attente',
  recu: 'Recu',
  en_traitement: 'En traitement',
  corrige: 'Corrige',
  erreur: 'Erreur',
  validee: 'Validee',
  rejetee: 'Rejetee',
  en_cours_verification: 'Verification en cours',
}

export default function StatusBadge({ status, variant, className }: StatusBadgeProps) {
  const resolvedVariant = variant || statusVariants[status] || 'default'
  const label = statusLabels[status] || status

  const variantStyles = {
    success: 'bg-green-50 text-green-700 border-green-200',
    warning: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    error: 'bg-red-50 text-red-700 border-red-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    default: 'bg-gray-50 text-gray-700 border-gray-200',
  }

  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
        variantStyles[resolvedVariant],
        className
      )}
    >
      {label}
    </span>
  )
}
