import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import LoginPage from './LoginPage'

// Mock useAuth hook
const mockLogin = vi.fn()
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    login: mockLogin,
    user: null,
    isLoading: false,
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => children,
}))

// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// Mock schemas - utilise le vrai module mais permet de verifier les appels
vi.mock('../schemas', async () => {
  const actual = await vi.importActual('../schemas')
  return actual
})

function renderLoginPage() {
  return render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>
  )
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render login form', () => {
    renderLoginPage()

    expect(screen.getByText('Hub Chantier')).toBeInTheDocument()
    expect(screen.getByText('Greg Construction')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Mot de passe')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Se connecter' })).toBeInTheDocument()
  })

  it('should show subtitle text', () => {
    renderLoginPage()
    expect(screen.getByText(/Connectez-vous pour acceder/)).toBeInTheDocument()
  })

  it('should update email input', async () => {
    const user = userEvent.setup()
    renderLoginPage()

    const emailInput = screen.getByLabelText('Email')
    await user.type(emailInput, 'test@example.com')

    expect(emailInput).toHaveValue('test@example.com')
  })

  it('should update password input', async () => {
    const user = userEvent.setup()
    renderLoginPage()

    const passwordInput = screen.getByLabelText('Mot de passe')
    await user.type(passwordInput, 'mypassword')

    expect(passwordInput).toHaveValue('mypassword')
  })

  it('should validate required email field with Zod', async () => {
    const user = userEvent.setup()
    renderLoginPage()

    // Soumettre sans email (seulement mot de passe)
    await user.type(screen.getByLabelText('Mot de passe'), 'password123')
    await user.click(screen.getByRole('button', { name: 'Se connecter' }))

    // Zod doit afficher une erreur de validation pour l'email
    await waitFor(() => {
      expect(screen.getByText('Ce champ est requis')).toBeInTheDocument()
    })
    // Login ne doit pas etre appele
    expect(mockLogin).not.toHaveBeenCalled()
  })

  it('should validate required password field with Zod', async () => {
    const user = userEvent.setup()
    renderLoginPage()

    // Soumettre sans mot de passe (seulement email)
    await user.type(screen.getByLabelText('Email'), 'test@example.com')
    await user.click(screen.getByRole('button', { name: 'Se connecter' }))

    // Zod doit afficher une erreur de validation pour le mot de passe
    await waitFor(() => {
      expect(screen.getByText('Ce champ est requis')).toBeInTheDocument()
    })
    // Login ne doit pas etre appele
    expect(mockLogin).not.toHaveBeenCalled()
  })

  it('should have email input type', () => {
    renderLoginPage()
    expect(screen.getByLabelText('Email')).toHaveAttribute('type', 'email')
  })

  it('should have password input type', () => {
    renderLoginPage()
    expect(screen.getByLabelText('Mot de passe')).toHaveAttribute('type', 'password')
  })

  it('should call login on form submit', async () => {
    const user = userEvent.setup()
    mockLogin.mockResolvedValue(undefined)

    renderLoginPage()

    await user.type(screen.getByLabelText('Email'), 'test@example.com')
    await user.type(screen.getByLabelText('Mot de passe'), 'password123')
    await user.click(screen.getByRole('button', { name: 'Se connecter' }))

    expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123')
  })

  it('should navigate after successful login', async () => {
    const user = userEvent.setup()
    mockLogin.mockResolvedValue(undefined)

    renderLoginPage()

    await user.type(screen.getByLabelText('Email'), 'test@example.com')
    await user.type(screen.getByLabelText('Mot de passe'), 'password123')
    await user.click(screen.getByRole('button', { name: 'Se connecter' }))

    // Wait for the async login to complete
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })

  it('should show error on login failure', async () => {
    const user = userEvent.setup()
    mockLogin.mockRejectedValue({
      response: { data: { detail: 'Invalid credentials' } },
    })

    renderLoginPage()

    await user.type(screen.getByLabelText('Email'), 'test@example.com')
    await user.type(screen.getByLabelText('Mot de passe'), 'wrongpassword')
    await user.click(screen.getByRole('button', { name: 'Se connecter' }))

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
    })
  })

  it('should show default error when no detail', async () => {
    const user = userEvent.setup()
    mockLogin.mockRejectedValue(new Error('Network'))

    renderLoginPage()

    await user.type(screen.getByLabelText('Email'), 'test@example.com')
    await user.type(screen.getByLabelText('Mot de passe'), 'password')
    await user.click(screen.getByRole('button', { name: 'Se connecter' }))

    await waitFor(() => {
      expect(screen.getByText('Erreur de connexion')).toBeInTheDocument()
    })
  })

  it('should have placeholder text', () => {
    renderLoginPage()
    expect(screen.getByPlaceholderText('votre@email.com')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('********')).toBeInTheDocument()
  })
})
