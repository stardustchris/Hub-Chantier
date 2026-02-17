/**
 * useSecuritySettings - Hook pour la gestion des parametres de securite.
 *
 * Extrait de SecuritySettingsPage la logique metier:
 * - Changement de mot de passe via POST /auth/change-password
 */

import { useState, useCallback } from 'react'
import api from '../services/api'
import type { ApiError } from '../types/api'

interface ChangePasswordResult {
  success: boolean
  isWrongOldPassword: boolean
}

interface UseSecuritySettingsReturn {
  isChangingPassword: boolean
  changePassword: (oldPassword: string, newPassword: string) => Promise<ChangePasswordResult>
}

export function useSecuritySettings(): UseSecuritySettingsReturn {
  const [isChangingPassword, setIsChangingPassword] = useState(false)

  const changePassword = useCallback(async (
    oldPassword: string,
    newPassword: string
  ): Promise<ChangePasswordResult> => {
    setIsChangingPassword(true)
    try {
      await api.post('/auth/change-password', {
        old_password: oldPassword,
        new_password: newPassword,
      })
      return { success: true, isWrongOldPassword: false }
    } catch (err) {
      const error = err as ApiError
      const isWrongOldPassword = error.response?.status === 400
      return { success: false, isWrongOldPassword }
    } finally {
      setIsChangingPassword(false)
    }
  }, [])

  return {
    isChangingPassword,
    changePassword,
  }
}

export default useSecuritySettings
