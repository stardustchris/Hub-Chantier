/**
 * Tooltip d'onboarding custom (remplacement react-joyride)
 * Design mobile-first, non-bloquant, avec overlay semi-transparent
 */

import { useEffect, useState } from 'react'
import { X, ChevronRight } from 'lucide-react'
import type { TourStep } from './tours'

interface OnboardingTooltipProps {
  step: TourStep
  currentStep: number
  totalSteps: number
  onNext: () => void
  onSkip: () => void
}

export default function OnboardingTooltip({
  step,
  currentStep,
  totalSteps,
  onNext,
  onSkip,
}: OnboardingTooltipProps) {
  const [position, setPosition] = useState({ top: 0, left: 0 })
  const [highlightRect, setHighlightRect] = useState<DOMRect | null>(null)

  useEffect(() => {
    const updatePosition = () => {
      const targetElement = document.querySelector(`[data-tour="${step.target}"]`)

      if (!targetElement) {
        console.warn(`Onboarding: Element with data-tour="${step.target}" not found`)
        return
      }

      const rect = targetElement.getBoundingClientRect()
      setHighlightRect(rect)

      // Calculer la position du tooltip selon placement
      const tooltipWidth = 320
      const tooltipHeight = 200
      const gap = 16

      let top = 0
      let left = 0

      switch (step.placement) {
        case 'bottom':
          top = rect.bottom + gap
          left = rect.left + rect.width / 2 - tooltipWidth / 2
          break
        case 'top':
          top = rect.top - tooltipHeight - gap
          left = rect.left + rect.width / 2 - tooltipWidth / 2
          break
        case 'right':
          top = rect.top + rect.height / 2 - tooltipHeight / 2
          left = rect.right + gap
          break
        case 'left':
          top = rect.top + rect.height / 2 - tooltipHeight / 2
          left = rect.left - tooltipWidth - gap
          break
        default:
          top = rect.bottom + gap
          left = rect.left
      }

      // Ajuster si hors écran
      if (left + tooltipWidth > window.innerWidth) {
        left = window.innerWidth - tooltipWidth - 16
      }
      if (left < 16) {
        left = 16
      }
      if (top + tooltipHeight > window.innerHeight) {
        top = window.innerHeight - tooltipHeight - 16
      }
      if (top < 16) {
        top = 16
      }

      setPosition({ top, left })
    }

    updatePosition()

    // Scroll pour rendre l'élément visible
    const targetElement = document.querySelector(`[data-tour="${step.target}"]`)
    targetElement?.scrollIntoView({ behavior: 'smooth', block: 'center' })

    // Repositionner sur resize/scroll
    window.addEventListener('resize', updatePosition)
    window.addEventListener('scroll', updatePosition, true)
    return () => {
      window.removeEventListener('resize', updatePosition)
      window.removeEventListener('scroll', updatePosition, true)
    }
  }, [step])

  const isLastStep = currentStep === totalSteps - 1

  return (
    <>
      {/* Overlay semi-transparent */}
      <div className="fixed inset-0 bg-black/40 z-[9998] pointer-events-auto" onClick={onSkip} />

      {/* Highlight sur l'élément ciblé */}
      {highlightRect && (
        <div
          className="fixed z-[9999] pointer-events-none"
          style={{
            top: highlightRect.top - 4,
            left: highlightRect.left - 4,
            width: highlightRect.width + 8,
            height: highlightRect.height + 8,
            border: '3px solid #10B981',
            borderRadius: '12px',
            boxShadow: '0 0 0 4px rgba(16, 185, 129, 0.2)',
          }}
        />
      )}

      {/* Tooltip */}
      <div
        role="dialog"
        aria-label={step.title}
        aria-modal="true"
        className="fixed z-[10000] bg-white rounded-2xl shadow-2xl p-6 pointer-events-auto"
        style={{
          top: `${position.top}px`,
          left: `${position.left}px`,
          width: '320px',
          maxWidth: 'calc(100vw - 32px)',
        }}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <div className="text-xs font-semibold text-primary-600 mb-1">
              ÉTAPE {currentStep + 1}/{totalSteps}
            </div>
            <h3 className="text-lg font-bold text-gray-900">{step.title}</h3>
          </div>
          <button
            onClick={onSkip}
            className="ml-2 min-w-[44px] min-h-[44px] flex items-center justify-center hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Fermer le guide"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Content */}
        <p className="text-gray-700 text-sm leading-relaxed mb-4">{step.content}</p>

        {/* Progress bar */}
        <div className="mb-4">
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-600 transition-all duration-300"
              style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={onSkip}
            className="flex-1 py-3 px-4 border border-gray-300 rounded-xl font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Passer
          </button>
          <button
            onClick={onNext}
            className="flex-1 py-3 px-4 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
          >
            {isLastStep ? 'Terminer' : 'Suivant'}
            {!isLastStep && <ChevronRight className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </>
  )
}
