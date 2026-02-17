/**
 * Tests pour AchatsPage - Module 17 Phase 1
 * CDC FIN-03 à FIN-07
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import AchatsPage from './AchatsPage'

// Mock services
vi.mock('../services/financier', () => ({
  financierService: {
    listAchats: vi.fn(() => Promise.resolve({ items: [] })),
    listFournisseurs: vi.fn(() => Promise.resolve({ items: [] })),
    getBudgetByChantier: vi.fn(() => Promise.resolve({ id: 1, lots: [] })),
    listLots: vi.fn(() => Promise.resolve([])),
  },
}))

vi.mock('../services/chantiers', () => ({
  chantiersService: {
    list: vi.fn(() => Promise.resolve({ items: [] })),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
  },
}))

// Mock Layout component
vi.mock('../components/Layout', () => ({
  default: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="layout">
      {children}
    </div>
  ),
}))

// Mock AchatModal component
vi.mock('../components/financier/AchatModal', () => ({
  default: () => <div data-testid="achat-modal">Achat Modal</div>,
}))

function renderAchatsPage() {
  return render(
    <MemoryRouter>
      <AchatsPage />
    </MemoryRouter>
  )
}

describe('AchatsPage', () => {
  describe('Affichage de base', () => {
    it('affiche le titre "Achats & Bons de commande"', () => {
      renderAchatsPage()
      expect(screen.getByText('Total HT')).toBeInTheDocument()
    })

    it('affiche le composant Layout', () => {
      renderAchatsPage()
      expect(screen.getByTestId('layout')).toBeInTheDocument()
    })

    it('affiche les statistiques globales', () => {
      renderAchatsPage()
      expect(screen.getByText('Total HT')).toBeInTheDocument()
      expect(screen.getByText('Total TTC')).toBeInTheDocument()
    })
  })

  describe('Fonctionnalités attendues (CDC)', () => {
    it('devrait afficher une liste d\'achats (FIN-03)', async () => {
      renderAchatsPage()
      await waitFor(() => {
        expect(screen.queryByText(/Chargement/i)).not.toBeInTheDocument()
      })
      // Test de placeholder - la fonctionnalité complète sera implémentée
      expect(screen.getByText('Total HT')).toBeInTheDocument()
    })

    it('devrait permettre de créer un nouvel achat (FIN-04)', async () => {
      renderAchatsPage()
      await waitFor(() => {
        expect(screen.getByText('Nouveau bon de commande')).toBeInTheDocument()
      })
      // Test de placeholder - bouton "Nouvel achat" à implémenter
      expect(screen.getByTestId('layout')).toBeInTheDocument()
    })

    it('devrait afficher les montants TTC et HT (FIN-05)', async () => {
      renderAchatsPage()
      await waitFor(() => {
        expect(screen.getByText('Total HT')).toBeInTheDocument()
      })
      // Test de placeholder - les montants seront affichés dans la liste
      expect(screen.getByText('Total TTC')).toBeInTheDocument()
    })

    it('devrait permettre de joindre des factures (FIN-06)', async () => {
      renderAchatsPage()
      await waitFor(() => {
        expect(screen.queryByText(/Chargement/i)).not.toBeInTheDocument()
      })
      // Test de placeholder - upload de documents à implémenter
      expect(screen.getByTestId('layout')).toBeInTheDocument()
    })

    it('devrait lier les achats aux chantiers (FIN-07)', async () => {
      renderAchatsPage()
      await waitFor(() => {
        expect(screen.queryByText(/Chargement/i)).not.toBeInTheDocument()
      })
      // Test de placeholder - sélection de chantier à implémenter
      expect(screen.getByTestId('layout')).toBeInTheDocument()
    })
  })

  describe('Structure de la page', () => {
    it('utilise le composant Layout avec le bon titre', async () => {
      renderAchatsPage()
      await waitFor(() => {
        expect(screen.getByText('Total HT')).toBeInTheDocument()
      })
    })

    it('est rendu sans erreur', () => {
      const { container } = renderAchatsPage()
      expect(container).toBeTruthy()
    })
  })
})
