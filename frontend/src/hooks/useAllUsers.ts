/**
 * useAllUsers - Hook pour charger la liste de tous les utilisateurs
 *
 * Utilisé par le Dashboard pour la résolution des mentions @.
 * Charge une page unique de 100 utilisateurs au montage.
 */

import { useState, useEffect } from 'react'
import { usersService } from '../services/users'
import type { User } from '../types'

interface UseAllUsersReturn {
  /** Liste des utilisateurs chargés */
  users: User[]
}

/**
 * Charge tous les utilisateurs (max 100) pour le matching des mentions @.
 * Silencieux en cas d'erreur : retourne une liste vide.
 */
export function useAllUsers(): UseAllUsersReturn {
  const [users, setUsers] = useState<User[]>([])

  useEffect(() => {
    usersService.list({ size: 100 }).then((res) => setUsers(res.items)).catch(() => {})
  }, [])

  return { users }
}

export default useAllUsers
