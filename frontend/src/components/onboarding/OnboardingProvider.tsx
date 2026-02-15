/**
 * OnboardingProvider - Gère l'état du tour guidé
 * Persiste la complétion dans localStorage par rôle
 */

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { TOURS } from './tours'
import OnboardingTooltip from './OnboardingTooltip'
import type { UserRole } from '../../types'

interface OnboardingContextValue {
  isActive: boolean
  isComplete: boolean
  startTour: () => void
  skipTour: () => void
  resetTour: () => void
}

const OnboardingContext = createContext<OnboardingContextValue | undefined>(undefined)

export function useOnboarding() {
  const context = useContext(OnboardingContext)
  if (!context) {
    throw new Error('useOnboarding must be used within OnboardingProvider')
  }
  return context
}

interface OnboardingProviderProps {
  children: ReactNode
}

export default function OnboardingProvider({ children }: OnboardingProviderProps) {
  const { user } = useAuth()
  const [isActive, setIsActive] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [isComplete, setIsComplete] = useState(false)

  const role = user?.role as UserRole | undefined
  const tour = role ? TOURS[role] : []

  // Charger l'état de complétion depuis localStorage
  useEffect(() => {
    if (!role) return

    const storageKey = `hub-onboarding-${role}-completed`
    const completed = localStorage.getItem(storageKey) === 'true'
    setIsComplete(completed)

    // Auto-start si pas encore complété et première connexion
    if (!completed && user) {
      const hasSeenWelcome = localStorage.getItem('hub-onboarding-welcome-shown')
      if (!hasSeenWelcome) {
        localStorage.setItem('hub-onboarding-welcome-shown', 'true')
        // Délai pour laisser le temps à la page de charger
        setTimeout(() => {
          setIsActive(true)
        }, 1000)
      }
    }
  }, [role, user])

  const startTour = useCallback(() => {
    setCurrentStep(0)
    setIsActive(true)
  }, [])

  const skipTour = useCallback(() => {
    setIsActive(false)
    setCurrentStep(0)
    if (role) {
      const storageKey = `hub-onboarding-${role}-completed`
      localStorage.setItem(storageKey, 'true')
      setIsComplete(true)
    }
  }, [role])

  const resetTour = useCallback(() => {
    if (role) {
      const storageKey = `hub-onboarding-${role}-completed`
      localStorage.removeItem(storageKey)
      setIsComplete(false)
      startTour()
    }
  }, [role, startTour])

  const handleNext = useCallback(() => {
    if (currentStep < tour.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      // Tour terminé
      skipTour()
    }
  }, [currentStep, tour.length, skipTour])

  const contextValue: OnboardingContextValue = {
    isActive,
    isComplete,
    startTour,
    skipTour,
    resetTour,
  }

  return (
    <OnboardingContext.Provider value={contextValue}>
      {children}

      {/* Afficher le tooltip si tour actif */}
      {isActive && tour.length > 0 && (
        <OnboardingTooltip
          step={tour[currentStep]}
          currentStep={currentStep}
          totalSteps={tour.length}
          onNext={handleNext}
          onSkip={skipTour}
        />
      )}
    </OnboardingContext.Provider>
  )
}
