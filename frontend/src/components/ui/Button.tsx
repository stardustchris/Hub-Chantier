/**
 * Button component - Composant bouton réutilisable avec variantes et états
 * Supporte les états loading, disabled, et différentes tailles/variantes
 */

import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react'
import { Loader2, type LucideIcon } from 'lucide-react'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  icon?: LucideIcon
  children: ReactNode
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      disabled = false,
      icon: Icon,
      children,
      className = '',
      type = 'button',
      ...props
    },
    ref
  ) => {
    // Base classes pour tous les boutons
    const baseClasses =
      'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'

    // Classes selon la variante
    const variantClasses = {
      primary: 'bg-primary text-white hover:bg-primary-hover active:bg-primary-active',
      secondary: 'bg-secondary text-white hover:bg-secondary-hover active:bg-secondary-active',
      outline:
        'border-2 border-primary text-primary hover:bg-primary-light active:bg-primary-lighter',
      ghost: 'text-neutral-text hover:bg-neutral-hover active:bg-neutral-active',
      danger: 'bg-danger text-white hover:bg-danger-hover active:bg-danger-active',
    }

    // Classes selon la taille (touch target minimum 44px Apple HIG)
    const sizeClasses = {
      sm: 'px-3 py-2 text-sm min-h-[40px]',
      md: 'px-4 py-2.5 text-base min-h-[44px]',
      lg: 'px-6 py-3 text-lg min-h-[48px]',
    }

    const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || loading}
        aria-busy={loading || undefined}
        className={classes}
        {...props}
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>{children}</span>
          </>
        ) : (
          <>
            {Icon && <Icon className="w-5 h-5" />}
            <span>{children}</span>
          </>
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'

export default Button
