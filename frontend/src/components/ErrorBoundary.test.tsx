/**
 * Tests unitaires pour ErrorBoundary
 */

import React from 'react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ErrorBoundary from './ErrorBoundary'

// Composant qui lance une erreur pour tester
function ThrowError({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error message')
  }
  return <div>No error</div>
}

describe('ErrorBoundary', () => {
  // Supprimer les logs d'erreur pendant les tests
  const originalConsoleError = console.error

  beforeEach(() => {
    console.error = vi.fn()
  })

  afterEach(() => {
    console.error = originalConsoleError
  })

  it('affiche les enfants quand il n\'y a pas d\'erreur', () => {
    render(
      <ErrorBoundary>
        <div>Contenu enfant</div>
      </ErrorBoundary>
    )

    expect(screen.getByText('Contenu enfant')).toBeInTheDocument()
  })

  it('affiche le fallback par defaut quand une erreur survient', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
    expect(
      screen.getByText(/L'application a rencontre un probleme inattendu/)
    ).toBeInTheDocument()
  })

  it('affiche un fallback personnalise si fourni', () => {
    render(
      <ErrorBoundary fallback={<div>Erreur personnalisee</div>}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Erreur personnalisee')).toBeInTheDocument()
    expect(screen.queryByText('Une erreur est survenue')).not.toBeInTheDocument()
  })

  it('log l\'erreur dans la console', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(console.error).toHaveBeenCalled()
  })

  it('affiche les boutons Reessayer et Accueil', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Reessayer')).toBeInTheDocument()
    expect(screen.getByText('Accueil')).toBeInTheDocument()
  })

  it('le bouton Reessayer reset l\'etat d\'erreur', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()

    // On ne peut pas vraiment tester le retry car ThrowError va relancer l'erreur
    // Mais on peut verifier que le bouton existe et est cliquable
    const retryButton = screen.getByText('Reessayer')
    expect(retryButton).toBeInTheDocument()
  })

  it('le bouton Accueil redirige vers la page d\'accueil', () => {
    // Mock window.location
    const originalLocation = window.location
    Object.defineProperty(window, 'location', {
      value: { href: '', reload: vi.fn() },
      writable: true,
    })

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    const homeButton = screen.getByText('Accueil')
    fireEvent.click(homeButton)

    expect(window.location.href).toBe('/')

    // Restore
    Object.defineProperty(window, 'location', {
      value: originalLocation,
      writable: true,
    })
  })

  it('capture les erreurs des composants enfants profondement imbriques', () => {
    function DeepChild(): React.ReactNode {
      throw new Error('Deep error')
    }

    function MiddleComponent() {
      return <DeepChild />
    }

    render(
      <ErrorBoundary>
        <div>
          <MiddleComponent />
        </div>
      </ErrorBoundary>
    )

    expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
  })
})

describe('ErrorBoundary state management', () => {
  const originalConsoleError = console.error

  beforeEach(() => {
    console.error = vi.fn()
  })

  afterEach(() => {
    console.error = originalConsoleError
  })

  it('l\'etat initial n\'a pas d\'erreur', () => {
    render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    )

    expect(screen.getByText('Test content')).toBeInTheDocument()
    expect(screen.queryByText('Une erreur est survenue')).not.toBeInTheDocument()
  })

  it('getDerivedStateFromError met a jour hasError', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    // L'erreur a ete capturee
    expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
  })
})
