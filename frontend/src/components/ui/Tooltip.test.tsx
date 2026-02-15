/**
 * Tests for Tooltip component
 * Vérifie le comportement hover (desktop) et long-press (mobile)
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import Tooltip from './Tooltip'

describe('Tooltip', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should render trigger element', () => {
    render(
      <Tooltip content="Test tooltip">
        <button>Hover me</button>
      </Tooltip>
    )

    expect(screen.getByRole('button', { name: 'Hover me' })).toBeInTheDocument()
  })

  it('should not show tooltip initially', () => {
    render(
      <Tooltip content="Test tooltip">
        <button>Hover me</button>
      </Tooltip>
    )

    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()
  })

  it('should show tooltip on hover after delay', async () => {
    const user = userEvent.setup()
    render(
      <Tooltip content="Test tooltip" hoverDelay={100}>
        <button>Hover me</button>
      </Tooltip>
    )

    const button = screen.getByRole('button', { name: 'Hover me' })
    await user.hover(button)

    // Tooltip ne doit pas apparaître immédiatement
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()

    // Tooltip doit apparaître après le délai
    await waitFor(() => {
      expect(screen.getByRole('tooltip')).toBeInTheDocument()
      expect(screen.getByText('Test tooltip')).toBeInTheDocument()
    }, { timeout: 500 })
  })

  it('should hide tooltip on mouse leave', async () => {
    const user = userEvent.setup()
    render(
      <Tooltip content="Test tooltip" hoverDelay={50}>
        <button>Hover me</button>
      </Tooltip>
    )

    const button = screen.getByRole('button', { name: 'Hover me' })
    await user.hover(button)

    await waitFor(() => {
      expect(screen.getByRole('tooltip')).toBeInTheDocument()
    }, { timeout: 500 })

    await user.unhover(button)

    await waitFor(() => {
      expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()
    })
  })

  it('should set aria-describedby when tooltip is visible', async () => {
    const user = userEvent.setup()
    render(
      <Tooltip content="Test tooltip" hoverDelay={50}>
        <button>Hover me</button>
      </Tooltip>
    )

    const button = screen.getByRole('button', { name: 'Hover me' })

    // Initialement pas d'aria-describedby
    expect(button).not.toHaveAttribute('aria-describedby')

    await user.hover(button)

    // Après affichage du tooltip, aria-describedby doit être défini
    await waitFor(() => {
      const tooltip = screen.getByRole('tooltip')
      expect(button).toHaveAttribute('aria-describedby', tooltip.id)
    }, { timeout: 500 })
  })

  it('should support different positions', async () => {
    const user = userEvent.setup()
    render(
      <Tooltip content="Test tooltip" position="top" hoverDelay={50}>
        <button>Hover me</button>
      </Tooltip>
    )

    const button = screen.getByRole('button', { name: 'Hover me' })
    await user.hover(button)

    await waitFor(() => {
      expect(screen.getByRole('tooltip')).toBeInTheDocument()
    }, { timeout: 500 })
  })

  it('should preserve original event handlers', async () => {
    const user = userEvent.setup()
    const onMouseEnter = vi.fn()
    const onMouseLeave = vi.fn()

    render(
      <Tooltip content="Test tooltip" hoverDelay={50}>
        <button onMouseEnter={onMouseEnter} onMouseLeave={onMouseLeave}>
          Hover me
        </button>
      </Tooltip>
    )

    const button = screen.getByRole('button', { name: 'Hover me' })

    await user.hover(button)
    expect(onMouseEnter).toHaveBeenCalled()

    await user.unhover(button)
    expect(onMouseLeave).toHaveBeenCalled()
  })
})
