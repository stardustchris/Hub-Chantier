/**
 * Tests pour StatsCard
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatsCard from './StatsCard'

describe('StatsCard', () => {
  it('affiche les valeurs par defaut', () => {
    render(<StatsCard />)

    expect(screen.getByText('Cette semaine')).toBeInTheDocument()
    expect(screen.getByText('Heures travaillees')).toBeInTheDocument()
    expect(screen.getByText('32h15')).toBeInTheDocument()
    expect(screen.getByText('Taches terminees')).toBeInTheDocument()
    expect(screen.getByText('8/12')).toBeInTheDocument()
  })

  it('affiche les heures travaillees personnalisees', () => {
    render(<StatsCard hoursWorked="40h00" />)

    expect(screen.getByText('40h00')).toBeInTheDocument()
  })

  it('affiche la progression des heures', () => {
    const { container } = render(<StatsCard hoursProgress={50} />)

    const progressBar = container.querySelector('[style*="width: 50%"]')
    expect(progressBar).toBeInTheDocument()
  })

  it('affiche les taches terminees', () => {
    render(<StatsCard tasksCompleted={5} tasksTotal={10} />)

    expect(screen.getByText('5/10')).toBeInTheDocument()
  })

  it('affiche 0 taches si non specifiees', () => {
    render(<StatsCard tasksCompleted={0} tasksTotal={0} />)

    expect(screen.getByText('0/0')).toBeInTheDocument()
  })

  it('affiche 100% de progression', () => {
    const { container } = render(<StatsCard hoursProgress={100} />)

    const progressBar = container.querySelector('[style*="width: 100%"]')
    expect(progressBar).toBeInTheDocument()
  })

  it('gere les valeurs extremes', () => {
    render(
      <StatsCard
        hoursWorked="168h00"
        hoursProgress={150}
        tasksCompleted={999}
        tasksTotal={1000}
      />
    )

    expect(screen.getByText('168h00')).toBeInTheDocument()
    expect(screen.getByText('999/1000')).toBeInTheDocument()
  })
})
