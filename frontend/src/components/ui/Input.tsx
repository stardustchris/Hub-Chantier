/**
 * Input component - Composant input réutilisable avec états visuels et accessibilité
 * Supporte les icônes, messages d'erreur, hint text, et tous les types HTML standard
 */

import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { type LucideIcon } from 'lucide-react'

export interface InputProps extends ComponentPropsWithoutRef<'input'> {
  /** Label affiché au-dessus de l'input */
  label?: string
  /** Message d'erreur (déclenche l'état error) */
  error?: string
  /** Texte d'aide affiché sous l'input */
  hint?: string
  /** Icône affichée à gauche de l'input */
  icon?: LucideIcon
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      type = 'text',
      error,
      hint,
      icon: Icon,
      required = false,
      disabled = false,
      className = '',
      id,
      ...props
    },
    ref
  ) => {
    // Génération d'un ID unique si non fourni
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`
    const errorId = error ? `${inputId}-error` : undefined
    const hintId = hint ? `${inputId}-hint` : undefined

    // Base classes pour l'input
    const baseClasses =
      'w-full rounded-lg border px-4 py-2.5 text-base transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-neutral-disabled'

    // Classes selon l'état
    const stateClasses = error
      ? 'border-danger text-neutral-text placeholder:text-neutral-text-muted focus:border-danger focus:ring-danger'
      : 'border-neutral-border text-neutral-text placeholder:text-neutral-text-muted hover:border-neutral-border-dark focus:border-primary'

    // Ajout de padding si icône présente
    const iconPadding = Icon ? 'pl-11' : ''

    const inputClasses = `${baseClasses} ${stateClasses} ${iconPadding} ${className}`

    return (
      <div className="w-full">
        {/* Label */}
        {label && (
          <label
            htmlFor={inputId}
            className="mb-1.5 block text-sm font-medium text-neutral-text"
          >
            {label}
            {required && <span className="ml-1 text-danger">*</span>}
          </label>
        )}

        {/* Input container avec icône */}
        <div className="relative">
          {Icon && (
            <div className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2">
              <Icon className="h-5 w-5 text-neutral-text-muted" />
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            type={type}
            required={required}
            disabled={disabled}
            aria-invalid={error ? true : undefined}
            aria-describedby={
              errorId && hintId
                ? `${errorId} ${hintId}`
                : errorId || hintId || undefined
            }
            aria-required={required || undefined}
            className={inputClasses}
            {...props}
          />
        </div>

        {/* Message d'erreur */}
        {error && (
          <p
            id={errorId}
            className="mt-1.5 text-sm text-danger"
            role="alert"
          >
            {error}
          </p>
        )}

        {/* Texte d'aide */}
        {hint && !error && (
          <p
            id={hintId}
            className="mt-1.5 text-sm text-neutral-text-secondary"
          >
            {hint}
          </p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input
export { Input }
