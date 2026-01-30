import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { loginSchema, validateForm } from '../schemas'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setFieldErrors({})

    // Validation client avec Zod
    const validation = validateForm(loginSchema, { email, password })
    if (!validation.success) {
      setFieldErrors(validation.errors)
      return
    }

    setIsLoading(true)

    try {
      await login(email, password)
      navigate('/')
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } }
      setError(axiosError.response?.data?.detail || 'Erreur de connexion')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h1 className="text-center text-3xl font-bold text-primary-600">
            Hub Chantier
          </h1>
          <h2 className="mt-2 text-center text-xl text-gray-600">
            Greg Construction
          </h2>
          <p className="mt-4 text-center text-sm text-gray-500">
            Connectez-vous pour acceder a votre espace
          </p>
        </div>

        <form className="mt-8 space-y-6 card" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={`input mt-1 ${fieldErrors.email ? 'border-red-500' : ''}`}
                placeholder="votre@email.com"
                aria-invalid={!!fieldErrors.email}
                aria-describedby={fieldErrors.email ? 'email-error' : undefined}
              />
              {fieldErrors.email && (
                <p id="email-error" className="mt-1 text-sm text-red-600">
                  {fieldErrors.email}
                </p>
              )}
            </div>

            <div>
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Mot de passe
                </label>
                <Link
                  to="/forgot-password"
                  className="text-sm text-primary-600 hover:text-primary-500"
                >
                  Mot de passe oublié ?
                </Link>
              </div>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={`input mt-1 ${fieldErrors.password ? 'border-red-500' : ''}`}
                placeholder="********"
                aria-invalid={!!fieldErrors.password}
                aria-describedby={fieldErrors.password ? 'password-error' : undefined}
              />
              {fieldErrors.password && (
                <p id="password-error" className="mt-1 text-sm text-red-600">
                  {fieldErrors.password}
                </p>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full btn btn-primary py-3 disabled:opacity-50"
          >
            {isLoading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>
      </div>
    </div>
  )
}
