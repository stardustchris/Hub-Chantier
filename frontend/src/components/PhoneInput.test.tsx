/**
 * Tests pour PhoneInput
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import PhoneInput from './PhoneInput'

describe('PhoneInput', () => {
  it('affiche le label par defaut', () => {
    render(<PhoneInput value="" onChange={vi.fn()} />)

    expect(screen.getByText('Téléphone')).toBeInTheDocument()
  })

  it('affiche un label personnalise', () => {
    render(<PhoneInput value="" onChange={vi.fn()} label="Mobile" />)

    expect(screen.getByText('Mobile')).toBeInTheDocument()
  })

  it('affiche l\'asterisque si requis', () => {
    render(<PhoneInput value="" onChange={vi.fn()} required />)

    expect(screen.getByText('*')).toBeInTheDocument()
  })

  it('n\'affiche pas l\'asterisque si non requis', () => {
    render(<PhoneInput value="" onChange={vi.fn()} required={false} />)

    expect(screen.queryByText('*')).not.toBeInTheDocument()
  })

  it('affiche le placeholder personnalise', () => {
    render(<PhoneInput value="" onChange={vi.fn()} placeholder="Votre numero" />)

    expect(screen.getByPlaceholderText('Votre numero')).toBeInTheDocument()
  })

  it('affiche le placeholder par defaut', () => {
    render(<PhoneInput value="" onChange={vi.fn()} />)

    expect(screen.getByPlaceholderText('06 12 34 56 78')).toBeInTheDocument()
  })

  it('affiche la valeur initiale', () => {
    render(<PhoneInput value="0612345678" onChange={vi.fn()} />)

    expect(screen.getByDisplayValue('0612345678')).toBeInTheDocument()
  })

  it('appelle onChange lors de la saisie', () => {
    const onChange = vi.fn()
    render(<PhoneInput value="" onChange={onChange} />)

    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: '06' } })

    expect(onChange).toHaveBeenCalledWith('06')
  })

  it('filtre les caracteres non autorises', () => {
    const onChange = vi.fn()
    render(<PhoneInput value="" onChange={onChange} />)

    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: '06abcd12' } })

    expect(onChange).toHaveBeenCalledWith('0612')
  })

  it('autorise les chiffres', () => {
    const onChange = vi.fn()
    render(<PhoneInput value="" onChange={onChange} />)

    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: '0612345678' } })

    expect(onChange).toHaveBeenCalledWith('0612345678')
  })

  it('autorise le signe plus', () => {
    const onChange = vi.fn()
    render(<PhoneInput value="" onChange={onChange} />)

    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: '+33612345678' } })

    expect(onChange).toHaveBeenCalledWith('+33612345678')
  })

  it('autorise les espaces', () => {
    const onChange = vi.fn()
    render(<PhoneInput value="" onChange={onChange} />)

    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: '06 12 34' } })

    expect(onChange).toHaveBeenCalledWith('06 12 34')
  })

  it('autorise les tirets', () => {
    const onChange = vi.fn()
    render(<PhoneInput value="" onChange={onChange} />)

    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: '06-12-34' } })

    expect(onChange).toHaveBeenCalledWith('06-12-34')
  })

  it('desactive l\'input quand disabled est true', () => {
    render(<PhoneInput value="" onChange={vi.fn()} disabled />)

    const input = screen.getByRole('textbox')
    expect(input).toBeDisabled()
  })

  it('desactive le bouton pays quand disabled est true', () => {
    render(<PhoneInput value="" onChange={vi.fn()} disabled />)

    const countryButton = screen.getByRole('button')
    expect(countryButton).toBeDisabled()
  })

  it('affiche le drapeau France par defaut', () => {
    render(<PhoneInput value="" onChange={vi.fn()} />)

    expect(screen.getByText('🇫🇷')).toBeInTheDocument()
  })

  it('affiche le code pays +33 par defaut', () => {
    render(<PhoneInput value="" onChange={vi.fn()} />)

    expect(screen.getByText('+33')).toBeInTheDocument()
  })

  it('ouvre le dropdown pays au clic', () => {
    render(<PhoneInput value="" onChange={vi.fn()} />)

    const countryButton = screen.getByRole('button')
    fireEvent.click(countryButton)

    expect(screen.getByText('France')).toBeInTheDocument()
    expect(screen.getByText('Belgique')).toBeInTheDocument()
  })

  it('ferme le dropdown apres selection', () => {
    render(<PhoneInput value="" onChange={vi.fn()} />)

    const countryButton = screen.getByRole('button')
    fireEvent.click(countryButton)

    // Selectionner Belgique
    const belgiumOption = screen.getByText('Belgique')
    fireEvent.click(belgiumOption)

    // Le dropdown devrait etre ferme
    expect(screen.queryByText('Suisse')).not.toBeInTheDocument()
  })

  it('change le code pays apres selection', () => {
    render(<PhoneInput value="" onChange={vi.fn()} />)

    const countryButton = screen.getByRole('button')
    fireEvent.click(countryButton)

    const belgiumOption = screen.getByText('Belgique')
    fireEvent.click(belgiumOption)

    expect(screen.getByText('+32')).toBeInTheDocument()
    expect(screen.getByText('🇧🇪')).toBeInTheDocument()
  })

  it('n\'affiche pas d\'erreur avant interaction', () => {
    render(<PhoneInput value="abc" onChange={vi.fn()} />)

    // Pas d'erreur affichee car pas encore touche
    expect(screen.queryByText(/Format de téléphone invalide/)).not.toBeInTheDocument()
  })

  it('affiche une erreur apres blur si numero invalide', async () => {
    render(<PhoneInput value="123" onChange={vi.fn()} />)

    const input = screen.getByRole('textbox')
    fireEvent.blur(input)

    await waitFor(() => {
      expect(screen.getByText(/trop court/)).toBeInTheDocument()
    })
  })

  it('n\'affiche pas d\'erreur pour un numero valide', async () => {
    render(<PhoneInput value="0612345678" onChange={vi.fn()} />)

    const input = screen.getByRole('textbox')
    fireEvent.blur(input)

    await waitFor(() => {
      expect(screen.queryByText(/trop court/)).not.toBeInTheDocument()
    })
  })

  it('applique la classe CSS personnalisee', () => {
    const { container } = render(<PhoneInput value="" onChange={vi.fn()} className="custom-class" />)

    expect(container.querySelector('.custom-class')).toBeInTheDocument()
  })

  it('formate le numero au blur si valide', () => {
    const onChange = vi.fn()
    render(<PhoneInput value="0612345678" onChange={onChange} />)

    const input = screen.getByRole('textbox')
    fireEvent.blur(input)

    // Le numero devrait etre formate
    expect(onChange).toHaveBeenCalled()
  })

  it('ne formate pas le numero au blur si invalide', () => {
    const onChange = vi.fn()
    render(<PhoneInput value="123" onChange={onChange} />)

    const input = screen.getByRole('textbox')
    fireEvent.blur(input)

    // onChange ne devrait pas etre appele pour le formatage
    expect(onChange).not.toHaveBeenCalled()
  })

  it('remplace le code pays si deja present', () => {
    const onChange = vi.fn()
    render(<PhoneInput value="+33612345678" onChange={onChange} />)

    const countryButton = screen.getByRole('button')
    fireEvent.click(countryButton)

    const belgiumOption = screen.getByText('Belgique')
    fireEvent.click(belgiumOption)

    expect(onChange).toHaveBeenCalledWith('+32612345678')
  })

  it('n\'ouvre pas le dropdown si disabled', () => {
    render(<PhoneInput value="" onChange={vi.fn()} disabled />)

    const countryButton = screen.getByRole('button')
    fireEvent.click(countryButton)

    expect(screen.queryByText('France')).not.toBeInTheDocument()
  })

  it('detecte le pays automatiquement avec +32', () => {
    render(<PhoneInput value="+32475123456" onChange={vi.fn()} />)

    // Le drapeau belge devrait etre affiche
    expect(screen.getByText('🇧🇪')).toBeInTheDocument()
  })

  it('detecte le pays automatiquement avec +41', () => {
    render(<PhoneInput value="+41791234567" onChange={vi.fn()} />)

    // Le drapeau suisse devrait etre affiche
    expect(screen.getByText('🇨🇭')).toBeInTheDocument()
  })
})
