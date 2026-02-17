/**
 * useResetPassword - Hook pour la reinitialisation de mot de passe.
 *
 * Extrait de ResetPasswordPage la logique metier:
 * - Appel API POST /auth/reset-password avec le token et le nouveau mot de passe
 */

import { useState, useCallback } from 'react'
import api from '../services/api'
import type { ApiError } from '../types/api'

interface ResetPasswordResult {
  success: boolean
  errorStatus?: number
}

interface UseResetPasswordReturn {
  isLoading: boolean
  resetPassword: (token: string, newPassword: string) => Promise<ResetPasswordResult>
}

export function useResetPassword(): UseResetPasswordReturn {
  const [isLoading, setIsLoading] = useState(false)

  const resetPassword = useCallback(async (token: string, newPassword: string): Promise<ResetPasswordResult> => {
    setIsLoading(true)
    try {
      await api.post('/auth/reset-password', {
        token,
        new_password: newPassword,
      })
      return { success: true }
    } catch (err) {
      const error = err as ApiError
      return { success: false, errorStatus: error.response?.status }
    } finally {
      setIsLoading(false)
    }
  }, [])

  return {
    isLoading,
    resetPassword,
  }
}

export default useResetPassword
