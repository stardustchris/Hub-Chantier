/**
 * useCreateChantier - Hook pour la creation d'un chantier avec contacts et phases.
 *
 * Extrait de ChantiersListPage la logique de creation et de listing:
 * - Chargement de tous les chantiers (pour les compteurs de statut)
 * - Fonction de listing paginee (pour useListPage)
 * - Creation d'un chantier avec ses contacts et phases associes
 */

import { useState, useEffect, useCallback } from 'react'
import { chantiersService } from '../services/chantiers'
import { logger } from '../services/logger'
import type { Chantier, ChantierCreate, ChantierStatut, PaginatedResponse } from '../types'
import type { TempContact, TempPhase } from '../components/chantiers'

interface ListParams {
  page?: number
  size?: number
  search?: string
  statut?: ChantierStatut
  [key: string]: unknown
}

interface UseCreateChantierReturn {
  allChantiers: Chantier[]
  loadAllChantiers: () => Promise<void>
  fetchChantiers: (params: ListParams) => Promise<PaginatedResponse<Chantier>>
  handleCreateChantier: (
    data: ChantierCreate,
    contacts: TempContact[],
    phases: TempPhase[],
    onSuccess: () => Promise<void>
  ) => Promise<void>
}

export function useCreateChantier(): UseCreateChantierReturn {
  const [allChantiers, setAllChantiers] = useState<Chantier[]>([])

  const loadAllChantiers = useCallback(async () => {
    try {
      const response = await chantiersService.list({ size: 500 })
      setAllChantiers(response.items)
    } catch (error) {
      logger.error('Error loading all chantiers', error, { context: 'useCreateChantier' })
    }
  }, [])

  useEffect(() => {
    loadAllChantiers()
  }, [loadAllChantiers])

  const fetchChantiers = useCallback((params: ListParams): Promise<PaginatedResponse<Chantier>> => {
    return chantiersService.list({
      page: params.page,
      size: params.size,
      search: params.search,
      statut: params.statut as ChantierStatut | undefined,
    })
  }, [])

  const handleCreateChantier = useCallback(async (
    data: ChantierCreate,
    contacts: TempContact[],
    phases: TempPhase[],
    onSuccess: () => Promise<void>
  ) => {
    // Create the chantier
    const chantier = await chantiersService.create(data)

    // Create contacts (ignore empty ones)
    for (const contact of contacts) {
      if (contact.nom && contact.telephone) {
        await chantiersService.addContact(chantier.id, {
          nom: contact.nom,
          telephone: contact.telephone,
          profession: contact.profession || undefined,
        })
      }
    }

    // Create phases (ignore empty ones)
    for (const phase of phases) {
      if (phase.nom) {
        await chantiersService.addPhase(chantier.id, {
          nom: phase.nom,
          date_debut: phase.date_debut || undefined,
          date_fin: phase.date_fin || undefined,
        })
      }
    }

    await loadAllChantiers()
    await onSuccess()
  }, [loadAllChantiers])

  return {
    allChantiers,
    loadAllChantiers,
    fetchChantiers,
    handleCreateChantier,
  }
}

export default useCreateChantier
