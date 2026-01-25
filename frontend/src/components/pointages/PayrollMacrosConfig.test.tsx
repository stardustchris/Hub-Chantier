/**
 * Tests pour PayrollMacrosConfig
 * FDH-18: Macros de paie - Calculs automatises parametrables
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import PayrollMacrosConfig from './PayrollMacrosConfig'
import type { PayrollConfig } from './PayrollMacrosConfig'

describe('PayrollMacrosConfig', () => {
  const defaultConfig: PayrollConfig = {
    heures_sup_seuil: 35,
    heures_sup_majoration: 25,
    heures_sup_majoration_2: 50,
    heures_sup_seuil_2: 43,
    panier_repas: 10.30,
    transport_zone_1: 3.50,
    transport_zone_2: 7.00,
    transport_zone_3: 10.50,
    prime_intemperies: 15.00,
    macros: [],
  }

  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onSave: vi.fn(),
    config: defaultConfig,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendu', () => {
    it('n\'affiche rien quand isOpen est false', () => {
      render(<PayrollMacrosConfig {...defaultProps} isOpen={false} />)
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('affiche le modal quand isOpen est true', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('affiche le titre du modal', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      expect(screen.getByText('Configuration des macros de paie')).toBeInTheDocument()
    })

    it('affiche les onglets', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      expect(screen.getByText('Heures supplementaires')).toBeInTheDocument()
      expect(screen.getByText('Indemnites')).toBeInTheDocument()
      expect(screen.getByText('Macros personnalisees')).toBeInTheDocument()
    })

    it('affiche l\'onglet Heures supplementaires par defaut', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      expect(screen.getByLabelText('Seuil heures normales')).toBeInTheDocument()
    })
  })

  describe('Onglet Heures supplementaires', () => {
    it('affiche les champs de configuration', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      expect(screen.getByLabelText('Seuil heures normales')).toHaveValue(35)
      expect(screen.getByLabelText('Majoration premiere tranche')).toHaveValue(25)
      expect(screen.getByLabelText('Seuil deuxieme tranche')).toHaveValue(43)
      expect(screen.getByLabelText('Majoration deuxieme tranche')).toHaveValue(50)
    })

    it('affiche l\'apercu du calcul', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      expect(screen.getByText('Apercu du calcul')).toBeInTheDocument()
      expect(screen.getByText('0 - 35h : taux normal')).toBeInTheDocument()
    })

    it('permet de modifier les valeurs', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      const input = screen.getByLabelText('Seuil heures normales')
      fireEvent.change(input, { target: { value: '39' } })
      expect(input).toHaveValue(39)
    })
  })

  describe('Onglet Indemnites', () => {
    it('affiche les champs d\'indemnites', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      fireEvent.click(screen.getByText('Indemnites'))

      expect(screen.getByLabelText('Montant panier repas')).toHaveValue(10.3)
      expect(screen.getByLabelText('Montant prime intemperies')).toHaveValue(15)
    })

    it('affiche les zones de transport', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      fireEvent.click(screen.getByText('Indemnites'))

      expect(screen.getByLabelText('Transport zone 1')).toHaveValue(3.5)
      expect(screen.getByLabelText('Transport zone 2')).toHaveValue(7)
      expect(screen.getByLabelText('Transport zone 3')).toHaveValue(10.5)
    })
  })

  describe('Onglet Macros personnalisees', () => {
    it('affiche le message vide quand pas de macros', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      fireEvent.click(screen.getByText('Macros personnalisees'))

      expect(screen.getByText('Aucune macro personnalisee')).toBeInTheDocument()
    })

    it('affiche le bouton d\'ajout de macro', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      fireEvent.click(screen.getByText('Macros personnalisees'))

      expect(screen.getByText('Ajouter une macro')).toBeInTheDocument()
    })

    it('ajoute une nouvelle macro au clic', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      fireEvent.click(screen.getByText('Macros personnalisees'))
      fireEvent.click(screen.getByText('Ajouter une macro'))

      expect(screen.getByDisplayValue('Nouvelle macro')).toBeInTheDocument()
    })

    it('affiche les macros existantes', () => {
      const configWithMacros = {
        ...defaultConfig,
        macros: [
          {
            id: 'macro-1',
            nom: 'Prime anciennete',
            type: 'fixe' as const,
            variable: 'total',
            valeur: 50,
            actif: true,
          },
        ],
      }
      render(<PayrollMacrosConfig {...defaultProps} config={configWithMacros} />)
      fireEvent.click(screen.getByText('Macros personnalisees'))

      expect(screen.getByDisplayValue('Prime anciennete')).toBeInTheDocument()
    })

    it('permet de supprimer une macro', () => {
      const configWithMacros = {
        ...defaultConfig,
        macros: [
          {
            id: 'macro-1',
            nom: 'Test macro',
            type: 'fixe' as const,
            variable: 'total',
            valeur: 10,
            actif: true,
          },
        ],
      }
      render(<PayrollMacrosConfig {...defaultProps} config={configWithMacros} />)
      fireEvent.click(screen.getByText('Macros personnalisees'))

      const deleteButton = screen.getByLabelText('Supprimer Test macro')
      fireEvent.click(deleteButton)

      expect(screen.queryByDisplayValue('Test macro')).not.toBeInTheDocument()
    })
  })

  describe('Actions', () => {
    it('appelle onClose au clic sur le backdrop', () => {
      const onClose = vi.fn()
      render(<PayrollMacrosConfig {...defaultProps} onClose={onClose} />)

      const backdrop = document.querySelector('.bg-black\\/50')
      if (backdrop) {
        fireEvent.click(backdrop)
      }
      expect(onClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur le bouton X', () => {
      const onClose = vi.fn()
      render(<PayrollMacrosConfig {...defaultProps} onClose={onClose} />)

      fireEvent.click(screen.getByLabelText('Fermer'))
      expect(onClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur Annuler', () => {
      const onClose = vi.fn()
      render(<PayrollMacrosConfig {...defaultProps} onClose={onClose} />)

      fireEvent.click(screen.getByText('Annuler'))
      expect(onClose).toHaveBeenCalled()
    })

    it('appelle onSave au clic sur Enregistrer', () => {
      const onSave = vi.fn()
      render(<PayrollMacrosConfig {...defaultProps} onSave={onSave} />)

      fireEvent.click(screen.getByText('Enregistrer'))
      expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
        heures_sup_seuil: 35,
      }))
    })

    it('affiche l\'indicateur de modifications non enregistrees', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      const input = screen.getByLabelText('Seuil heures normales')
      fireEvent.change(input, { target: { value: '40' } })

      expect(screen.getByText('Modifications non enregistrees')).toBeInTheDocument()
    })
  })

  describe('Accessibilite', () => {
    it('le dialog a les attributs ARIA corrects', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-modal', 'true')
      expect(dialog).toHaveAttribute('aria-labelledby', 'macros-title')
    })

    it('les champs ont des labels accessibles', () => {
      render(<PayrollMacrosConfig {...defaultProps} />)
      expect(screen.getByLabelText('Seuil heures normales')).toBeInTheDocument()
      expect(screen.getByLabelText('Majoration premiere tranche')).toBeInTheDocument()
    })
  })
})
