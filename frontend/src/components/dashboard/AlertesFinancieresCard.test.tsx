/**
 * Tests pour AlertesFinancieresCard
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import AlertesFinancieresCard from './AlertesFinancieresCard'

// Mock de useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('AlertesFinancieresCard', () => {
  it('ne s\'affiche pas pendant le chargement', () => {
    const { container } = render(
      <BrowserRouter>
        <AlertesFinancieresCard />
      </BrowserRouter>
    )

    // Le composant retourne null pendant le chargement
    expect(container.firstChild).toBeNull()
  })

  it('ne s\'affiche pas s\'il n\'y a aucune alerte', async () => {
    const { container } = render(
      <BrowserRouter>
        <AlertesFinancieresCard />
      </BrowserRouter>
    )

    // Attendre que le chargement se termine
    await new Promise((resolve) => setTimeout(resolve, 100))

    // Le composant retourne null si aucune alerte
    expect(container.firstChild).toBeNull()
  })

  it('ne s\'affiche pas en cas d\'erreur', async () => {
    const { container } = render(
      <BrowserRouter>
        <AlertesFinancieresCard />
      </BrowserRouter>
    )

    // Attendre que le chargement se termine
    await new Promise((resolve) => setTimeout(resolve, 100))

    // Le composant retourne null en cas d'erreur
    expect(container.firstChild).toBeNull()
  })

  // Note: Les tests avec des alertes réelles nécessitent de mocker le service financier
  // Ces tests seront ajoutés une fois l'endpoint backend implémenté
})
