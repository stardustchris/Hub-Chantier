/**
 * useAcceptInvitation - Hook pour l'acceptation d'une invitation.
 *
 * Extrait de AcceptInvitationPage la logique metier:
 * - Chargement des informations de l'invitation via GET /auth/invitation/:token
 * - Acceptation de l'invitation via POST /auth/accept-invitation
 */

import { useState, useCallback } from 'react'
import api from '../services/api'
import type { ApiError, InvitationInfo } from '../types/api'

interface FetchInvitationResult {
  success: boolean
  errorStatus?: number
}

interface AcceptInvitationResult {
  success: boolean
  errorStatus?: number
}

interface UseAcceptInvitationReturn {
  invitationInfo: InvitationInfo | null
  isLoadingInfo: boolean
  isLoading: boolean
  fetchInvitationInfo: (token: string) => Promise<FetchInvitationResult>
  acceptInvitation: (token: string, password: string) => Promise<AcceptInvitationResult>
}

export function useAcceptInvitation(): UseAcceptInvitationReturn {
  const [invitationInfo, setInvitationInfo] = useState<InvitationInfo | null>(null)
  const [isLoadingInfo, setIsLoadingInfo] = useState(true)
  const [isLoading, setIsLoading] = useState(false)

  const fetchInvitationInfo = useCallback(async (token: string): Promise<FetchInvitationResult> => {
    setIsLoadingInfo(true)
    try {
      const response = await api.get(`/auth/invitation/${token}`)
      setInvitationInfo(response.data)
      return { success: true }
    } catch (err) {
      const error = err as ApiError
      return { success: false, errorStatus: error.response?.status }
    } finally {
      setIsLoadingInfo(false)
    }
  }, [])

  const acceptInvitation = useCallback(async (token: string, password: string): Promise<AcceptInvitationResult> => {
    setIsLoading(true)
    try {
      await api.post('/auth/accept-invitation', { token, password })
      return { success: true }
    } catch (err) {
      const error = err as ApiError
      return { success: false, errorStatus: error.response?.status }
    } finally {
      setIsLoading(false)
    }
  }, [])

  return {
    invitationInfo,
    isLoadingInfo,
    isLoading,
    fetchInvitationInfo,
    acceptInvitation,
  }
}

export default useAcceptInvitation
