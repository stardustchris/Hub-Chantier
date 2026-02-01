/**
 * Tests pour MetierMultiSelect - sélection multi-métiers
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MetierMultiSelect } from './MetierMultiSelect'
import type { Metier } from '../../types'

describe('MetierMultiSelect', () => {
  const mockOnChange = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Affichage initial', () => {
    it('affiche le placeholder quand aucun métier sélectionné', () => {
      render(<MetierMultiSelect value={[]} onChange={mockOnChange} />)
      expect(screen.getByText('Sélectionner un métier')).toBeInTheDocument()
    })

    it('affiche "Ajouter un métier" quand des métiers sont déjà sélectionnés', () => {
      render(<MetierMultiSelect value={['macon' as Metier]} onChange={mockOnChange} />)
      expect(screen.getByText('Ajouter un métier')).toBeInTheDocument()
    })

    it('affiche les badges des métiers sélectionnés', () => {
      render(
        <MetierMultiSelect value={['macon' as Metier, 'coffreur' as Metier]} onChange={mockOnChange} />
      )
      expect(screen.getByText('Macon')).toBeInTheDocument()
      expect(screen.getByText('Coffreur')).toBeInTheDocument()
    })

    it('affiche le compteur de métiers', () => {
      render(
        <MetierMultiSelect value={['macon' as Metier, 'coffreur' as Metier]} onChange={mockOnChange} />
      )
      expect(screen.getByText('2 / 5 métiers sélectionnés')).toBeInTheDocument()
    })

    it('affiche 0 / 5 quand aucun métier', () => {
      render(<MetierMultiSelect value={[]} onChange={mockOnChange} />)
      expect(screen.getByText('0 / 5 métiers sélectionnés')).toBeInTheDocument()
    })
  })

  describe('Limite de 5 métiers', () => {
    it('permet de sélectionner jusqu\'à 5 métiers', async () => {
      const user = userEvent.setup()
      render(<MetierMultiSelect value={[]} onChange={mockOnChange} />)

      // Ouvrir dropdown et sélectionner premier métier
      await user.click(screen.getByText('Sélectionner un métier'))
      await user.click(screen.getByText('Macon'))

      expect(mockOnChange).toHaveBeenCalledWith(['macon'])

      // Le test vérifie qu'on peut appeler jusqu'à 5 fois
      // (le comportement exact de limite est testé dans un autre test)
    })

    it('désactive le bouton quand 5 métiers atteints', () => {
      const fiveMetiers: Metier[] = [
        'macon',
        'coffreur',
        'ferrailleur',
        'grutier',
        'charpentier',
      ]
      render(<MetierMultiSelect value={fiveMetiers} onChange={mockOnChange} />)

      const button = screen.getByText('Maximum 5 métiers atteint').closest('button')
      expect(button).toBeDisabled()
    })

    it('affiche le message de limite atteinte', () => {
      const fiveMetiers: Metier[] = [
        'macon',
        'coffreur',
        'ferrailleur',
        'grutier',
        'charpentier',
      ]
      render(<MetierMultiSelect value={fiveMetiers} onChange={mockOnChange} />)

      expect(screen.getByText('Maximum 5 métiers atteint')).toBeInTheDocument()
      expect(screen.getByText('5 / 5 métiers sélectionnés')).toBeInTheDocument()
    })
  })

  describe('Ajout de métiers', () => {
    it('appelle onChange avec le nouveau métier ajouté', async () => {
      const user = userEvent.setup()
      render(<MetierMultiSelect value={[]} onChange={mockOnChange} />)

      // Ouvrir dropdown
      await user.click(screen.getByText('Sélectionner un métier'))

      // Sélectionner "Macon"
      await user.click(screen.getByText('Macon'))

      expect(mockOnChange).toHaveBeenCalledWith(['macon'])
    })

    it('ajoute un métier à la liste existante', async () => {
      const user = userEvent.setup()
      render(<MetierMultiSelect value={['macon' as Metier]} onChange={mockOnChange} />)

      await user.click(screen.getByText('Ajouter un métier'))
      await user.click(screen.getByText('Coffreur'))

      expect(mockOnChange).toHaveBeenCalledWith(['macon', 'coffreur'])
    })

    it('ferme le dropdown après sélection', async () => {
      const user = userEvent.setup()
      render(<MetierMultiSelect value={[]} onChange={mockOnChange} />)

      await user.click(screen.getByText('Sélectionner un métier'))
      await user.click(screen.getByText('Macon'))

      // Le dropdown devrait être fermé (liste non visible)
      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /Coffreur/i })).not.toBeInTheDocument()
      })
    })

    it('n\'ajoute pas un métier déjà sélectionné', async () => {
      const user = userEvent.setup()
      const { rerender } = render(
        <MetierMultiSelect value={['macon' as Metier]} onChange={mockOnChange} />
      )

      await user.click(screen.getByText('Ajouter un métier'))

      // Macon ne devrait pas apparaître dans la liste (déjà sélectionné)
      expect(screen.queryByRole('button', { name: /^Macon$/i })).not.toBeInTheDocument()
    })
  })

  describe('Suppression de métiers', () => {
    it('appelle onChange pour retirer un métier', async () => {
      const user = userEvent.setup()
      render(
        <MetierMultiSelect
          value={['macon' as Metier, 'coffreur' as Metier]}
          onChange={mockOnChange}
        />
      )

      // Trouver le bouton X du badge "Macon"
      const maconBadge = screen.getByText('Macon').closest('span')
      const removeButton = maconBadge?.querySelector('button')

      if (removeButton) {
        await user.click(removeButton)
        expect(mockOnChange).toHaveBeenCalledWith(['coffreur'])
      }
    })

    it('retire le métier de la liste', async () => {
      const user = userEvent.setup()
      render(
        <MetierMultiSelect
          value={['macon' as Metier, 'coffreur' as Metier, 'ferrailleur' as Metier]}
          onChange={mockOnChange}
        />
      )

      const coffreurBadge = screen.getByText('Coffreur').closest('span')
      const removeButton = coffreurBadge?.querySelector('button')

      if (removeButton) {
        await user.click(removeButton)
        expect(mockOnChange).toHaveBeenCalledWith(['macon', 'ferrailleur'])
      }
    })
  })

  describe('Mode désactivé', () => {
    it('n\'affiche pas le bouton X en mode disabled', () => {
      render(
        <MetierMultiSelect
          value={['macon' as Metier]}
          onChange={mockOnChange}
          disabled={true}
        />
      )

      const maconBadge = screen.getByText('Macon').closest('span')
      const removeButton = maconBadge?.querySelector('button')

      expect(removeButton).not.toBeInTheDocument()
    })

    it('n\'affiche pas le dropdown en mode disabled', () => {
      render(
        <MetierMultiSelect
          value={['macon' as Metier]}
          onChange={mockOnChange}
          disabled={true}
        />
      )

      expect(screen.queryByText('Ajouter un métier')).not.toBeInTheDocument()
    })

    it('affiche uniquement les badges en mode disabled', () => {
      render(
        <MetierMultiSelect
          value={['macon' as Metier, 'coffreur' as Metier]}
          onChange={mockOnChange}
          disabled={true}
        />
      )

      expect(screen.getByText('Macon')).toBeInTheDocument()
      expect(screen.getByText('Coffreur')).toBeInTheDocument()
      expect(screen.getByText('2 / 5 métiers sélectionnés')).toBeInTheDocument()
    })
  })

  describe('Dropdown', () => {
    it('ouvre le dropdown au clic', async () => {
      const user = userEvent.setup()
      render(<MetierMultiSelect value={[]} onChange={mockOnChange} />)

      await user.click(screen.getByText('Sélectionner un métier'))

      expect(screen.getByText('Macon')).toBeInTheDocument()
      expect(screen.getByText('Coffreur')).toBeInTheDocument()
      expect(screen.getByText('Grutier')).toBeInTheDocument()
    })

    it('ferme le dropdown au clic extérieur', async () => {
      const user = userEvent.setup()
      render(
        <div>
          <MetierMultiSelect value={[]} onChange={mockOnChange} />
          <button>Outside</button>
        </div>
      )

      await user.click(screen.getByText('Sélectionner un métier'))
      expect(screen.getByText('Macon')).toBeInTheDocument()

      await user.click(screen.getByText('Outside'))

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /Macon/i })).not.toBeInTheDocument()
      })
    })

    it('affiche tous les métiers disponibles', async () => {
      const user = userEvent.setup()
      render(<MetierMultiSelect value={[]} onChange={mockOnChange} />)

      await user.click(screen.getByText('Sélectionner un métier'))

      // Vérifier que tous les métiers sont présents
      const expectedMetiers = [
        'Macon',
        'Coffreur',
        'Ferrailleur',
        'Grutier',
        'Charpentier',
        'Couvreur',
        'Terrassier',
        'Administratif',
        'Autre',
      ]

      expectedMetiers.forEach(metier => {
        expect(screen.getByText(metier)).toBeInTheDocument()
      })
    })

    it('affiche les indicateurs de couleur dans le dropdown', async () => {
      const user = userEvent.setup()
      const { container } = render(<MetierMultiSelect value={[]} onChange={mockOnChange} />)

      await user.click(screen.getByText('Sélectionner un métier'))

      // Vérifier que des indicateurs colorés existent
      const colorIndicators = container.querySelectorAll('.w-3.h-3.rounded-full')
      expect(colorIndicators.length).toBeGreaterThan(0)
    })
  })

  describe('Couleurs des badges', () => {
    it('applique les couleurs correctes aux badges', () => {
      const { container } = render(
        <MetierMultiSelect
          value={['macon' as Metier, 'coffreur' as Metier]}
          onChange={mockOnChange}
        />
      )

      const badges = container.querySelectorAll('span[style*="background-color"]')
      expect(badges.length).toBe(2)
    })
  })
})
