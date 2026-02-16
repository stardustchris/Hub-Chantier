/**
 * DemoContext - Contexte pour le mode démonstration
 * Permet aux utilisateurs de tester l'app avec des données fictives
 * sans impact sur les données réelles
 */

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react'
import { demoData, type DemoData } from '../data/demoData'

interface DemoContextValue {
  isDemoMode: boolean
  enableDemoMode: () => void
  disableDemoMode: () => void
  demoData: DemoData
}

const DemoContext = createContext<DemoContextValue | undefined>(undefined)

export function useDemo() {
  const context = useContext(DemoContext)
  if (!context) {
    throw new Error('useDemo must be used within DemoProvider')
  }
  return context
}

interface DemoProviderProps {
  children: ReactNode
}

const STORAGE_KEY = 'hub_demo_mode'

export function DemoProvider({ children }: DemoProviderProps) {
  // Charger l'état depuis localStorage
  const [isDemoMode, setIsDemoMode] = useState<boolean>(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored === 'true'
  })

  // Persister dans localStorage à chaque changement
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(isDemoMode))
  }, [isDemoMode])

  const enableDemoMode = useCallback(() => {
    setIsDemoMode(true)
  }, [])

  const disableDemoMode = useCallback(() => {
    setIsDemoMode(false)
  }, [])

  const contextValue: DemoContextValue = {
    isDemoMode,
    enableDemoMode,
    disableDemoMode,
    demoData,
  }

  return <DemoContext.Provider value={contextValue}>{children}</DemoContext.Provider>
}
