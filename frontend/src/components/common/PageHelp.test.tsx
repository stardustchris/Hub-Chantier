/**
 * Tests for PageHelp component
 * Vérifie l'affichage du panneau d'aide contextuel et les hints progressifs
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { vi } from 'vitest'
import PageHelp from './PageHelp'

// Mock du hook useProgressiveHint
vi.mock('../../hooks/useProgressiveHint', () => ({
  useProgressiveHint: () => ({
    shouldShowHint: vi.fn(() => true),
    recordVisit: vi.fn(),
    getVisitCount: vi.fn(() => 1),
    resetVisits: vi.fn(),
  }),
}))

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('PageHelp', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('should render help button', () => {
    renderWithRouter(<PageHelp />)

    const button = screen.getByRole('button', { name: /aide contextuelle/i })
    expect(button).toBeInTheDocument()
  })

  it('should show pulsing badge for new visitors', () => {
    renderWithRouter(<PageHelp />)

    // Le badge pulsant doit être présent
    const button = screen.getByRole('button', { name: /aide contextuelle/i })
    const badge = button.querySelector('span[aria-hidden="true"]')
    expect(badge).toBeInTheDocument()
  })

  it('should open help panel on click', async () => {
    const user = userEvent.setup()
    renderWithRouter(<PageHelp />)

    const button = screen.getByRole('button', { name: /aide contextuelle/i })
    await user.click(button)

    // Le panneau doit s'ouvrir
    await waitFor(() => {
      expect(screen.getByRole('complementary', { name: /aide contextuelle/i })).toBeInTheDocument()
    })
  })

  it('should display help content for current page', async () => {
    const user = userEvent.setup()
    renderWithRouter(<PageHelp />)

    const button = screen.getByRole('button', { name: /aide contextuelle/i })
    await user.click(button)

    await waitFor(() => {
      // Vérifier que le titre de la page d'accueil est affiché
      expect(screen.getByText('Tableau de bord')).toBeInTheDocument()
    })
  })

  it('should close help panel on close button click', async () => {
    const user = userEvent.setup()
    renderWithRouter(<PageHelp />)

    const openButton = screen.getByRole('button', { name: /aide contextuelle/i })
    await user.click(openButton)

    await waitFor(() => {
      expect(screen.getByRole('complementary')).toBeInTheDocument()
    })

    const closeButton = screen.getByRole('button', { name: /fermer/i })
    await user.click(closeButton)

    await waitFor(() => {
      expect(screen.queryByRole('complementary')).not.toBeInTheDocument()
    })
  })

  it('should close help panel on backdrop click', async () => {
    const user = userEvent.setup()
    renderWithRouter(<PageHelp />)

    const openButton = screen.getByRole('button', { name: /aide contextuelle/i })
    await user.click(openButton)

    await waitFor(() => {
      expect(screen.getByRole('complementary')).toBeInTheDocument()
    })

    // Cliquer sur le backdrop (l'élément parent du panneau)
    const backdrop = screen.getByRole('complementary').parentElement
    if (backdrop) {
      await user.click(backdrop)

      await waitFor(() => {
        expect(screen.queryByRole('complementary')).not.toBeInTheDocument()
      })
    }
  })

  it('should block body scroll when panel is open', async () => {
    const user = userEvent.setup()
    renderWithRouter(<PageHelp />)

    const originalOverflow = document.body.style.overflow

    const button = screen.getByRole('button', { name: /aide contextuelle/i })
    await user.click(button)

    await waitFor(() => {
      expect(document.body.style.overflow).toBe('hidden')
    })

    const closeButton = screen.getByRole('button', { name: /fermer/i })
    await user.click(closeButton)

    await waitFor(() => {
      expect(document.body.style.overflow).toBe(originalOverflow)
    })
  })

  it('should display help sections', async () => {
    const user = userEvent.setup()
    renderWithRouter(<PageHelp />)

    const button = screen.getByRole('button', { name: /aide contextuelle/i })
    await user.click(button)

    await waitFor(() => {
      // Vérifier les sections d'aide de la page d'accueil
      expect(screen.getByText("Vue d'ensemble")).toBeInTheDocument()
      expect(screen.getByText('Pointer')).toBeInTheDocument()
    })
  })

  it('should have correct ARIA attributes', async () => {
    const user = userEvent.setup()
    renderWithRouter(<PageHelp />)

    const button = screen.getByRole('button', { name: /aide contextuelle/i })

    // Vérifier aria-expanded=false initialement
    expect(button).toHaveAttribute('aria-expanded', 'false')

    await user.click(button)

    // Vérifier aria-expanded=true après ouverture
    expect(button).toHaveAttribute('aria-expanded', 'true')

    // Vérifier les attributs du panneau
    await waitFor(() => {
      const panel = screen.getByRole('complementary')
      expect(panel).toHaveAttribute('aria-label', 'Aide contextuelle')
    })
  })

  it('should show fallback content for unknown routes', async () => {
    const user = userEvent.setup()

    // Mock useLocation pour retourner une route inconnue
    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom')
      return {
        ...actual,
        useLocation: () => ({ pathname: '/unknown-route' }),
      }
    })

    renderWithRouter(<PageHelp />)

    const button = screen.getByRole('button', { name: /aide contextuelle/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('Aide')).toBeInTheDocument()
      expect(screen.getByText('Assistance')).toBeInTheDocument()
    })
  })
})
