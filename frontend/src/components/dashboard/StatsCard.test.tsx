/**
 * Tests pour StatsCard
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatsCard from './StatsCard'

describe('StatsCard', () => {
  it('affiche les valeurs par defaut', () => {
    render(<StatsCard />)

    expect(screen.getByText('Heures travaillees')).toBeInTheDocument()
    expect(screen.getByText('Semaine en cours')).toBeInTheDocument()
    expect(screen.getByText('Jours travailles (mois)')).toBeInTheDocument()
    expect(screen.getByText('Conges pris (annee)')).toBeInTheDocument()
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

  it('affiche les jours travailles du mois', () => {
    render(<StatsCard joursTravailesMois={15} joursTotalMois={22} />)

    expect(screen.getByText('15')).toBeInTheDocument()
    expect(screen.getByText('/22')).toBeInTheDocument()
  })

  it('affiche les conges pris', () => {
    render(<StatsCard congesPris={3.5} congesTotal={25} />)

    expect(screen.getByText('3.5')).toBeInTheDocument()
    expect(screen.getByText('/25j')).toBeInTheDocument()
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
        joursTravailesMois={30}
        joursTotalMois={31}
        congesPris={25}
        congesTotal={25}
      />
    )

    expect(screen.getByText('168h00')).toBeInTheDocument()
    expect(screen.getByText('30')).toBeInTheDocument()
  })
})
