/**
 * Modal component - Composant modal accessible avec backdrop, animations et focus trap
 * Supporte la fermeture au clic backdrop et Escape, avec gestion du focus
 */

import { useEffect, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { X } from 'lucide-react'
import { useFocusTrap } from '../../hooks/useFocusTrap'

export interface ModalProps {
  /** Contrôle la visibilité de la modal */
  isOpen: boolean
  /** Callback appelé lors de la fermeture */
  onClose: () => void
  /** Titre de la modal */
  title: string
  /** Contenu de la modal */
  children: ReactNode
  /** Taille de la modal */
  size?: 'sm' | 'md' | 'lg' | 'xl'
  /** Classes CSS additionnelles */
  className?: string
}

const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  className = '',
}: ModalProps) => {
  const containerRef = useFocusTrap({ enabled: isOpen, onClose })

  // Bloquer le scroll du body quand la modal est ouverte
  useEffect(() => {
    if (isOpen) {
      const originalStyle = window.getComputedStyle(document.body).overflow
      document.body.style.overflow = 'hidden'
      return () => {
        document.body.style.overflow = originalStyle
      }
    }
  }, [isOpen])

  // Ne rien rendre si fermée
  if (!isOpen) return null

  // Classes de taille
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  }

  // Gestion du clic sur le backdrop
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  const modalId = `modal-${Math.random().toString(36).substr(2, 9)}`
  const titleId = `${modalId}-title`

  const modalContent = (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 motion-reduce:transition-none"
      onClick={handleBackdropClick}
      style={{
        animation: 'fadeIn 200ms ease-out',
      }}
    >
      <div
        ref={containerRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className={`
          relative w-full ${sizeClasses[size]}
          rounded-2xl bg-neutral-surface-primary shadow-xl
          motion-reduce:transition-none
          ${className}
        `}
        style={{
          animation: 'scaleIn 200ms ease-out',
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-neutral-border px-6 py-4">
          <h2
            id={titleId}
            className="text-xl font-semibold text-neutral-text"
          >
            {title}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-neutral-text-secondary transition-colors hover:bg-neutral-hover hover:text-neutral-text focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
            aria-label="Fermer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4">{children}</div>
      </div>

      {/* Animations CSS injectées */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes scaleIn {
          from {
            opacity: 0;
            transform: scale(0.95);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          @keyframes fadeIn {
            from, to {
              opacity: 1;
            }
          }

          @keyframes scaleIn {
            from, to {
              opacity: 1;
              transform: scale(1);
            }
          }
        }
      `}</style>
    </div>
  )

  return createPortal(modalContent, document.body)
}

Modal.displayName = 'Modal'

export default Modal
export { Modal }
