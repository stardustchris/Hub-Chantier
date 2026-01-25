/**
 * Tests pour QuickActions
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import QuickActions from './QuickActions'

describe('QuickActions', () => {
  it('affiche les actions par defaut', () => {
    render(<QuickActions />)

    expect(screen.getByText('Actions rapides')).toBeInTheDocument()
    expect(screen.getByText('Mes heures')).toBeInTheDocument()
    expect(screen.getByText('Mes taches')).toBeInTheDocument()
    expect(screen.getByText('Documents')).toBeInTheDocument()
    expect(screen.getByText('Photo')).toBeInTheDocument()
  })

  it('affiche des actions personnalisees', () => {
    const customActions = [
      { id: 'test1', label: 'Action 1', icon: 'clock' as const, color: 'blue' },
      { id: 'test2', label: 'Action 2', icon: 'check' as const, color: 'green' },
    ]

    render(<QuickActions actions={customActions} />)

    expect(screen.getByText('Action 1')).toBeInTheDocument()
    expect(screen.getByText('Action 2')).toBeInTheDocument()
    expect(screen.queryByText('Mes heures')).not.toBeInTheDocument()
  })

  it('appelle onActionClick au clic', () => {
    const onActionClick = vi.fn()
    render(<QuickActions onActionClick={onActionClick} />)

    const hoursButton = screen.getByText('Mes heures').closest('button')
    fireEvent.click(hoursButton!)

    expect(onActionClick).toHaveBeenCalledWith('hours')
  })

  it('appelle onClick de l\'action si defini', () => {
    const actionOnClick = vi.fn()
    const customActions = [
      { id: 'custom', label: 'Custom', icon: 'camera' as const, color: 'orange', onClick: actionOnClick },
    ]

    render(<QuickActions actions={customActions} />)

    const button = screen.getByText('Custom').closest('button')
    fireEvent.click(button!)

    expect(actionOnClick).toHaveBeenCalled()
  })

  it('appelle les deux callbacks si definis', () => {
    const actionOnClick = vi.fn()
    const onActionClick = vi.fn()
    const customActions = [
      { id: 'both', label: 'Both', icon: 'file' as const, color: 'purple', onClick: actionOnClick },
    ]

    render(<QuickActions actions={customActions} onActionClick={onActionClick} />)

    const button = screen.getByText('Both').closest('button')
    fireEvent.click(button!)

    expect(actionOnClick).toHaveBeenCalled()
    expect(onActionClick).toHaveBeenCalledWith('both')
  })

  it('gere les differentes couleurs', () => {
    const colorActions = [
      { id: '1', label: 'Blue', icon: 'clock' as const, color: 'blue' },
      { id: '2', label: 'Green', icon: 'check' as const, color: 'green' },
      { id: '3', label: 'Purple', icon: 'file' as const, color: 'purple' },
      { id: '4', label: 'Orange', icon: 'camera' as const, color: 'orange' },
    ]

    render(<QuickActions actions={colorActions} />)

    expect(screen.getByText('Blue')).toBeInTheDocument()
    expect(screen.getByText('Green')).toBeInTheDocument()
    expect(screen.getByText('Purple')).toBeInTheDocument()
    expect(screen.getByText('Orange')).toBeInTheDocument()
  })

  it('utilise la couleur par defaut pour une couleur inconnue', () => {
    const unknownColorAction = [
      { id: 'unknown', label: 'Unknown', icon: 'clock' as const, color: 'unknown' },
    ]

    render(<QuickActions actions={unknownColorAction} />)

    expect(screen.getByText('Unknown')).toBeInTheDocument()
  })

  it('rend correctement sans actions', () => {
    render(<QuickActions actions={[]} />)

    expect(screen.getByText('Actions rapides')).toBeInTheDocument()
  })
})
