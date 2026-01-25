/**
 * Tests pour TodayPlanningCard
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import TodayPlanningCard from './TodayPlanningCard'

const renderWithRouter = (props = {}) => {
  return render(
    <MemoryRouter>
      <TodayPlanningCard {...props} />
    </MemoryRouter>
  )
}

describe('TodayPlanningCard', () => {
  it('affiche le titre Mon planning aujourd\'hui', () => {
    renderWithRouter()

    expect(screen.getByText("Mon planning aujourd'hui")).toBeInTheDocument()
  })

  it('affiche le lien vers la semaine', () => {
    renderWithRouter()

    expect(screen.getByText('Voir semaine →')).toBeInTheDocument()
  })

  it('affiche les creneaux par defaut', () => {
    renderWithRouter()

    // Villa Moderne apparait 2 fois (matin et apres-midi)
    expect(screen.getAllByText('Villa Moderne - Lyon 3eme')).toHaveLength(2)
    expect(screen.getByText('Pause dejeuner')).toBeInTheDocument()
  })

  it('affiche les horaires des creneaux', () => {
    const slots = [
      {
        id: '1',
        startTime: '09:00',
        endTime: '12:30',
        period: 'morning' as const,
        siteName: 'Test Site',
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('09:00 - 12:30')).toBeInTheDocument()
  })

  it('affiche Matin pour les creneaux du matin', () => {
    const slots = [
      {
        id: '1',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Matin Site',
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('Matin')).toBeInTheDocument()
  })

  it('affiche Apres-midi pour les creneaux de l\'apres-midi', () => {
    const slots = [
      {
        id: '1',
        startTime: '14:00',
        endTime: '18:00',
        period: 'afternoon' as const,
        siteName: 'Apres-midi Site',
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('Apres-midi')).toBeInTheDocument()
  })

  it('affiche l\'adresse du chantier', () => {
    const slots = [
      {
        id: '1',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Test',
        siteAddress: '123 Rue Test, Paris',
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('123 Rue Test, Paris')).toBeInTheDocument()
  })

  it('affiche le statut En cours', () => {
    const slots = [
      {
        id: '1',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Test',
        status: 'in_progress' as const,
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('En cours')).toBeInTheDocument()
  })

  it('affiche le statut Planifie', () => {
    const slots = [
      {
        id: '1',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Test',
        status: 'planned' as const,
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('Planifie')).toBeInTheDocument()
  })

  it('affiche le statut Termine', () => {
    const slots = [
      {
        id: '1',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Test',
        status: 'completed' as const,
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('Termine')).toBeInTheDocument()
  })

  it('affiche les taches assignees', () => {
    const slots = [
      {
        id: '1',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Test',
        tasks: [{ id: 't1', name: 'Tache importante', priority: 'high' as const }],
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('Taches assignees :')).toBeInTheDocument()
    expect(screen.getByText('Tache importante')).toBeInTheDocument()
  })

  it('affiche la priorite Urgent', () => {
    const slots = [
      {
        id: '1',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Test',
        tasks: [{ id: 't1', name: 'Tache urgente', priority: 'urgent' as const }],
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('Urgent')).toBeInTheDocument()
  })

  it('affiche la priorite Haute', () => {
    const slots = [
      {
        id: '1',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Test',
        tasks: [{ id: 't1', name: 'Task', priority: 'high' as const }],
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('Haute')).toBeInTheDocument()
  })

  it('affiche la priorite Moyenne', () => {
    const slots = [
      {
        id: '1',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Test',
        tasks: [{ id: 't1', name: 'Task', priority: 'medium' as const }],
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('Moyenne')).toBeInTheDocument()
  })

  it('affiche la priorite Basse', () => {
    const slots = [
      {
        id: '1',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Test',
        tasks: [{ id: 't1', name: 'Task', priority: 'low' as const }],
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('Basse')).toBeInTheDocument()
  })

  it('affiche les boutons Itineraire et Appeler', () => {
    const slots = [
      {
        id: '1',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Test',
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('Itineraire')).toBeInTheDocument()
    expect(screen.getByText('Appeler')).toBeInTheDocument()
  })

  it('appelle onNavigate au clic sur Itineraire', () => {
    const onNavigate = vi.fn()
    const slots = [
      {
        id: 'slot-1',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Test',
      },
    ]

    renderWithRouter({ slots, onNavigate })

    fireEvent.click(screen.getByText('Itineraire'))

    expect(onNavigate).toHaveBeenCalledWith('slot-1')
  })

  it('appelle onCall au clic sur Appeler', () => {
    const onCall = vi.fn()
    const slots = [
      {
        id: 'slot-2',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Test',
      },
    ]

    renderWithRouter({ slots, onCall })

    fireEvent.click(screen.getByText('Appeler'))

    expect(onCall).toHaveBeenCalledWith('slot-2')
  })

  it('appelle onChantierClick au clic sur le nom du chantier', () => {
    const onChantierClick = vi.fn()
    const slots = [
      {
        id: '1',
        chantierId: 'ch-123',
        startTime: '08:00',
        endTime: '12:00',
        period: 'morning' as const,
        siteName: 'Chantier Cliquable',
      },
    ]

    renderWithRouter({ slots, onChantierClick })

    fireEvent.click(screen.getByText('Chantier Cliquable'))

    expect(onChantierClick).toHaveBeenCalledWith('ch-123')
  })

  it('gere une liste vide de creneaux', () => {
    renderWithRouter({ slots: [] })

    expect(screen.getByText("Mon planning aujourd'hui")).toBeInTheDocument()
  })

  it('affiche la pause dejeuner correctement', () => {
    const slots = [
      {
        id: 'break',
        startTime: '12:00',
        endTime: '13:00',
        period: 'break' as const,
      },
    ]

    renderWithRouter({ slots })

    expect(screen.getByText('12:00 - 13:00')).toBeInTheDocument()
    expect(screen.getByText('Pause dejeuner')).toBeInTheDocument()
  })

  it('n\'affiche pas les boutons pour la pause', () => {
    const slots = [
      {
        id: 'break',
        startTime: '12:00',
        endTime: '13:00',
        period: 'break' as const,
      },
    ]

    renderWithRouter({ slots })

    expect(screen.queryByText('Itineraire')).not.toBeInTheDocument()
    expect(screen.queryByText('Appeler')).not.toBeInTheDocument()
  })
})
