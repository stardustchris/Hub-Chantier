/**
 * Tests pour TeamCard
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import TeamCard from './TeamCard'

describe('TeamCard', () => {
  it('affiche les membres par defaut', () => {
    render(<TeamCard />)

    expect(screen.getByText('Equipe du jour')).toBeInTheDocument()
    expect(screen.getByText('Marc Dubois')).toBeInTheDocument()
    expect(screen.getByText('Chef de chantier')).toBeInTheDocument()
    expect(screen.getByText('Luc Martin')).toBeInTheDocument()
    expect(screen.getByText('Macon')).toBeInTheDocument()
    expect(screen.getByText('Thomas Bernard')).toBeInTheDocument()
    expect(screen.getByText('Coffreur')).toBeInTheDocument()
  })

  it('affiche les initiales des membres', () => {
    render(<TeamCard />)

    expect(screen.getByText('MD')).toBeInTheDocument() // Marc Dubois
    expect(screen.getByText('LM')).toBeInTheDocument() // Luc Martin
    expect(screen.getByText('TB')).toBeInTheDocument() // Thomas Bernard
  })

  it('affiche des membres personnalises', () => {
    const customMembers = [
      { id: '1', firstName: 'Jean', lastName: 'Dupont', role: 'Electricien', color: '#ff0000' },
      { id: '2', firstName: 'Marie', lastName: 'Curie', role: 'Ingenieur', color: '#00ff00' },
    ]

    render(<TeamCard members={customMembers} />)

    expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
    expect(screen.getByText('Electricien')).toBeInTheDocument()
    expect(screen.getByText('JD')).toBeInTheDocument()
    expect(screen.getByText('Marie Curie')).toBeInTheDocument()
    expect(screen.getByText('Ingenieur')).toBeInTheDocument()
    expect(screen.getByText('MC')).toBeInTheDocument()
  })

  it('affiche le bouton telephone pour les membres avec numero', () => {
    const membersWithPhone = [
      { id: '1', firstName: 'Test', lastName: 'User', role: 'Test', color: '#000', phone: '+33123456789' },
    ]

    render(<TeamCard members={membersWithPhone} />)

    const phoneButton = screen.getByRole('button')
    expect(phoneButton).toBeInTheDocument()
  })

  it('n\'affiche pas le bouton telephone pour les membres sans numero', () => {
    const membersWithoutPhone = [
      { id: '1', firstName: 'Test', lastName: 'User', role: 'Test', color: '#000' },
    ]

    render(<TeamCard members={membersWithoutPhone} />)

    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('appelle onCall au clic sur le bouton telephone', () => {
    const onCall = vi.fn()
    const membersWithPhone = [
      { id: 'member-1', firstName: 'Test', lastName: 'User', role: 'Test', color: '#000', phone: '+33123456789' },
    ]

    render(<TeamCard members={membersWithPhone} onCall={onCall} />)

    const phoneButton = screen.getByRole('button')
    fireEvent.click(phoneButton)

    expect(onCall).toHaveBeenCalledWith('member-1')
  })

  it('gere une liste vide de membres', () => {
    render(<TeamCard members={[]} />)

    expect(screen.getByText('Equipe du jour')).toBeInTheDocument()
  })

  it('gere les noms vides', () => {
    const membersWithEmptyNames = [
      { id: '1', firstName: '', lastName: '', role: 'Unknown', color: '#000' },
    ]

    render(<TeamCard members={membersWithEmptyNames} />)

    expect(screen.getByText('Unknown')).toBeInTheDocument()
  })

  it('applique la couleur du membre', () => {
    const memberWithColor = [
      { id: '1', firstName: 'Test', lastName: 'User', role: 'Test', color: '#ff5500' },
    ]

    const { container } = render(<TeamCard members={memberWithColor} />)

    const avatar = container.querySelector('[style*="background-color: rgb(255, 85, 0)"]')
    expect(avatar).toBeInTheDocument()
  })
})
