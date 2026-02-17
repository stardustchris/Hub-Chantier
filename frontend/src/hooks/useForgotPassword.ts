/**
 * useForgotPassword - Hook pour la demande de reinitialisation de mot de passe.
 *
 * Extrait de ForgotPasswordPage la logique metier:
 * - Envoi de l'email de reinitialisation via authService
 */

import { useState, useCallback } from 'react'
import { authService } from '../services/auth'

interface UseForgotPasswordReturn {
  isLoading: boolean
  emailSent: boolean
  requestPasswordReset: (email: string) => Promise<{ wasSuccess: boolean }>
  resetEmailSent: () => void
}

export function useForgotPassword(): UseForgotPasswordReturn {
  const [isLoading, setIsLoading] = useState(false)
  const [emailSent, setEmailSent] = useState(false)

  const requestPasswordReset = useCallback(async (email: string): Promise<{ wasSuccess: boolean }> => {
    setIsLoading(true)
    try {
      await authService.requestPasswordReset(email)
      setEmailSent(true)
      return { wasSuccess: true }
    } catch {
      // Pour des raisons de securite, on affiche toujours le meme message
      // meme si l'email n'existe pas dans la base
      setEmailSent(true)
      return { wasSuccess: false }
    } finally {
      setIsLoading(false)
    }
  }, [])

  const resetEmailSent = useCallback(() => {
    setEmailSent(false)
  }, [])

  return {
    isLoading,
    emailSent,
    requestPasswordReset,
    resetEmailSent,
  }
}

export default useForgotPassword
