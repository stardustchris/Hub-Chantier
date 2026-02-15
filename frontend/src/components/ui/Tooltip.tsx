/**
 * Tooltip component - Info-bulle contextuelle avec support desktop (hover) et mobile (long-press)
 * Affiche une aide contextuelle au survol ou au long-press sur les éléments
 */

import { useState, useRef, useEffect, cloneElement, type ReactElement } from 'react'

export interface TooltipProps {
  /** Texte à afficher dans le tooltip */
  content: string
  /** Élément déclencheur (doit accepter des props event handlers) */
  children: ReactElement
  /** Position du tooltip par rapport à l'élément */
  position?: 'top' | 'bottom' | 'left' | 'right'
  /** Délai avant affichage au hover (ms) */
  hoverDelay?: number
  /** Durée du long-press pour mobile (ms) */
  longPressDelay?: number
}

const Tooltip = ({
  content,
  children,
  position = 'top',
  hoverDelay = 300,
  longPressDelay = 500,
}: TooltipProps) => {
  const [isVisible, setIsVisible] = useState(false)
  const [coords, setCoords] = useState({ top: 0, left: 0 })
  const hoverTimeoutRef = useRef<number>()
  const longPressTimeoutRef = useRef<number>()
  const touchStartTimeRef = useRef<number>()
  const triggerRef = useRef<HTMLElement>(null)
  const tooltipId = useRef(`tooltip-${Math.random().toString(36).substr(2, 9)}`)

  // Calculer la position du tooltip
  const calculatePosition = (triggerElement: HTMLElement) => {
    const rect = triggerElement.getBoundingClientRect()
    const tooltipWidth = 200 // max-w-xs approximation
    const tooltipHeight = 40 // Hauteur approximative
    const gap = 8

    let top = 0
    let left = 0

    switch (position) {
      case 'top':
        top = rect.top - tooltipHeight - gap
        left = rect.left + rect.width / 2 - tooltipWidth / 2
        break
      case 'bottom':
        top = rect.bottom + gap
        left = rect.left + rect.width / 2 - tooltipWidth / 2
        break
      case 'left':
        top = rect.top + rect.height / 2 - tooltipHeight / 2
        left = rect.left - tooltipWidth - gap
        break
      case 'right':
        top = rect.top + rect.height / 2 - tooltipHeight / 2
        left = rect.right + gap
        break
    }

    // Ajuster si hors de l'écran
    const maxLeft = window.innerWidth - tooltipWidth - 16
    const maxTop = window.innerHeight - tooltipHeight - 16
    left = Math.max(16, Math.min(left, maxLeft))
    top = Math.max(16, Math.min(top, maxTop))

    setCoords({ top, left })
  }

  // Handlers pour desktop (hover)
  const handleMouseEnter = (_e: React.MouseEvent<HTMLElement>) => {
    clearTimeout(hoverTimeoutRef.current)
    hoverTimeoutRef.current = window.setTimeout(() => {
      if (triggerRef.current) {
        calculatePosition(triggerRef.current)
        setIsVisible(true)
      }
    }, hoverDelay)
  }

  const handleMouseLeave = () => {
    clearTimeout(hoverTimeoutRef.current)
    setIsVisible(false)
  }

  // Handlers pour mobile (long-press)
  const handleTouchStart = (_e: React.TouchEvent<HTMLElement>) => {
    touchStartTimeRef.current = Date.now()
    longPressTimeoutRef.current = window.setTimeout(() => {
      if (triggerRef.current) {
        calculatePosition(triggerRef.current)
        setIsVisible(true)
      }
    }, longPressDelay)
  }

  const handleTouchEnd = () => {
    clearTimeout(longPressTimeoutRef.current)
    const touchDuration = Date.now() - (touchStartTimeRef.current || 0)

    // Si c'est un tap court, ne pas afficher le tooltip
    if (touchDuration < longPressDelay) {
      setIsVisible(false)
    }
  }

  const handleTouchMove = () => {
    // Annuler le long-press si l'utilisateur déplace son doigt
    clearTimeout(longPressTimeoutRef.current)
  }

  // Cleanup des timeouts
  useEffect(() => {
    return () => {
      clearTimeout(hoverTimeoutRef.current)
      clearTimeout(longPressTimeoutRef.current)
    }
  }, [])

  // Fermer le tooltip au scroll/resize
  useEffect(() => {
    if (!isVisible) return

    const handleScrollOrResize = () => {
      setIsVisible(false)
    }

    window.addEventListener('scroll', handleScrollOrResize, true)
    window.addEventListener('resize', handleScrollOrResize)

    return () => {
      window.removeEventListener('scroll', handleScrollOrResize, true)
      window.removeEventListener('resize', handleScrollOrResize)
    }
  }, [isVisible])

  // Classes pour la flèche selon la position
  const arrowClasses = {
    top: 'bottom-[-6px] left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent border-t-gray-900',
    bottom: 'top-[-6px] left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent border-b-gray-900',
    left: 'right-[-6px] top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent border-l-gray-900',
    right: 'left-[-6px] top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent border-r-gray-900',
  }

  // Cloner l'enfant avec les event handlers et ref
  const enhancedChild = cloneElement(children, {
    ref: triggerRef,
    onMouseEnter: (e: React.MouseEvent<HTMLElement>) => {
      handleMouseEnter(e)
      children.props.onMouseEnter?.(e)
    },
    onMouseLeave: (e: React.MouseEvent<HTMLElement>) => {
      handleMouseLeave()
      children.props.onMouseLeave?.(e)
    },
    onTouchStart: (e: React.TouchEvent<HTMLElement>) => {
      handleTouchStart(e)
      children.props.onTouchStart?.(e)
    },
    onTouchEnd: (e: React.TouchEvent<HTMLElement>) => {
      handleTouchEnd()
      children.props.onTouchEnd?.(e)
    },
    onTouchMove: (e: React.TouchEvent<HTMLElement>) => {
      handleTouchMove()
      children.props.onTouchMove?.(e)
    },
    'aria-describedby': isVisible ? tooltipId.current : undefined,
  } as React.HTMLAttributes<HTMLElement>)

  return (
    <>
      {enhancedChild}
      {isVisible && (
        <div
          id={tooltipId.current}
          role="tooltip"
          className="fixed z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg max-w-xs pointer-events-none"
          style={{
            top: `${coords.top}px`,
            left: `${coords.left}px`,
            animation: 'tooltipFadeIn 150ms ease-out',
          }}
        >
          {content}
          <div
            className={`absolute w-0 h-0 border-4 ${arrowClasses[position]}`}
          />

          {/* Animations CSS injectées */}
          <style>{`
            @keyframes tooltipFadeIn {
              from {
                opacity: 0;
                transform: translateY(-4px);
              }
              to {
                opacity: 1;
                transform: translateY(0);
              }
            }

            @media (prefers-reduced-motion: reduce) {
              @keyframes tooltipFadeIn {
                from, to {
                  opacity: 1;
                  transform: translateY(0);
                }
              }
            }
          `}</style>
        </div>
      )}
    </>
  )
}

Tooltip.displayName = 'Tooltip'

export default Tooltip
