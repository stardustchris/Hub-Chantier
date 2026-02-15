/**
 * Tests pour StreakBadge
 */

import { render, screen } from '@testing-library/react'
import StreakBadge from './StreakBadge'

describe('StreakBadge', () => {
  it('should not render when streak is 0', () => {
    const { container } = render(<StreakBadge streak={0} />)
    expect(container.firstChild).toBeNull()
  })

  it('should render badge for 1 day', () => {
    render(<StreakBadge streak={1} />)
    expect(screen.getByText('1 jour')).toBeInTheDocument()
  })

  it('should render badge for multiple days', () => {
    render(<StreakBadge streak={7} />)
    expect(screen.getByText('7 jours')).toBeInTheDocument()
  })

  it('should apply gold styling for 5+ days', () => {
    const { container } = render(<StreakBadge streak={5} />)
    const badge = container.querySelector('.from-yellow-400')
    expect(badge).toBeInTheDocument()
  })

  it('should apply pulse animation for 10+ days', () => {
    const { container } = render(<StreakBadge streak={10} />)
    const badge = container.querySelector('.animate-pulse')
    expect(badge).toBeInTheDocument()
  })

  it('should apply platinum styling for 20+ days', () => {
    const { container } = render(<StreakBadge streak={20} />)
    const badge = container.querySelector('.from-gray-300')
    expect(badge).toBeInTheDocument()
  })
})
