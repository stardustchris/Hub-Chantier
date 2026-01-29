/**
 * Schemas de validation Zod pour le frontend
 *
 * Tous les schemas de validation sont centralises ici pour:
 * - Coherence des regles de validation
 * - Reutilisation entre les formulaires
 * - Messages d'erreur en francais
 */

import { z } from 'zod'
import type { UserRole } from '../types'

/** Valeurs de UserRole extraites pour réutilisation dans les schemas Zod */
const USER_ROLES: [UserRole, ...UserRole[]] = ['admin', 'conducteur', 'chef_chantier', 'compagnon']

// Messages d'erreur personnalises en francais
const errorMessages = {
  required: 'Ce champ est requis',
  email: 'Adresse email invalide',
  minLength: (min: number) => `Minimum ${min} caracteres`,
  maxLength: (max: number) => `Maximum ${max} caracteres`,
  phone: 'Numero de telephone invalide',
  url: 'URL invalide',
  positive: 'La valeur doit etre positive',
  date: 'Date invalide',
}

// Schema de validation pour la connexion
export const loginSchema = z.object({
  email: z
    .string()
    .min(1, errorMessages.required)
    .email(errorMessages.email),
  password: z
    .string()
    .min(1, errorMessages.required)
    .min(6, errorMessages.minLength(6)),
})

export type LoginFormData = z.infer<typeof loginSchema>

// Schema de validation pour l'inscription
export const registerSchema = z.object({
  email: z
    .string()
    .min(1, errorMessages.required)
    .email(errorMessages.email),
  password: z
    .string()
    .min(1, errorMessages.required)
    .min(8, 'Le mot de passe doit contenir au moins 8 caracteres')
    .regex(/[A-Z]/, 'Le mot de passe doit contenir au moins une majuscule')
    .regex(/[a-z]/, 'Le mot de passe doit contenir au moins une minuscule')
    .regex(/[0-9]/, 'Le mot de passe doit contenir au moins un chiffre'),
  confirmPassword: z
    .string()
    .min(1, errorMessages.required),
  nom: z
    .string()
    .min(1, errorMessages.required)
    .max(50, errorMessages.maxLength(50)),
  prenom: z
    .string()
    .min(1, errorMessages.required)
    .max(50, errorMessages.maxLength(50)),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Les mots de passe ne correspondent pas',
  path: ['confirmPassword'],
})

export type RegisterFormData = z.infer<typeof registerSchema>

// Schema de validation pour les utilisateurs
export const userSchema = z.object({
  nom: z
    .string()
    .min(1, errorMessages.required)
    .max(50, errorMessages.maxLength(50)),
  prenom: z
    .string()
    .min(1, errorMessages.required)
    .max(50, errorMessages.maxLength(50)),
  email: z
    .string()
    .min(1, errorMessages.required)
    .email(errorMessages.email),
  telephone: z
    .string()
    .regex(/^(\+33|0)[1-9](\d{2}){4}$/, errorMessages.phone)
    .optional()
    .or(z.literal('')),
  role: z.enum(USER_ROLES),
  metier: z
    .string()
    .max(100, errorMessages.maxLength(100))
    .optional(),
})

export type UserFormData = z.infer<typeof userSchema>

// Schema de validation pour les chantiers
// Aligné avec l'interface ChantierCreate de types/index.ts
export const chantierSchema = z.object({
  nom: z
    .string()
    .min(1, errorMessages.required)
    .max(100, errorMessages.maxLength(100)),
  adresse: z
    .string()
    .min(1, errorMessages.required)
    .max(200, errorMessages.maxLength(200)),
  couleur: z
    .string()
    .optional(),
  latitude: z
    .number()
    .optional(),
  longitude: z
    .number()
    .optional(),
  contact_nom: z
    .string()
    .max(100, errorMessages.maxLength(100))
    .optional(),
  contact_telephone: z
    .string()
    .regex(/^(\+33|0)[1-9](\d{2}){4}$/, errorMessages.phone)
    .optional()
    .or(z.literal('')),
  heures_estimees: z
    .number()
    .positive(errorMessages.positive)
    .optional(),
  date_debut_prevue: z.string().optional(),
  date_fin_prevue: z.string().optional(),
  description: z
    .string()
    .max(2000, errorMessages.maxLength(2000))
    .optional(),
})

export type ChantierFormData = z.infer<typeof chantierSchema>

// Schema de validation pour les reservations
// Aligné avec l'interface ReservationCreate de types/logistique.ts
export const reservationSchema = z.object({
  ressource_id: z
    .number()
    .min(1, 'Veuillez selectionner une ressource'),
  chantier_id: z
    .number()
    .min(1, 'Veuillez selectionner un chantier'),
  date_reservation: z.string().min(1, errorMessages.required),
  heure_debut: z
    .string()
    .regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Format heure invalide (HH:MM)'),
  heure_fin: z
    .string()
    .regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Format heure invalide (HH:MM)'),
  commentaire: z
    .string()
    .max(500, errorMessages.maxLength(500))
    .optional(),
}).refine((data) => data.heure_fin > data.heure_debut, {
  message: "L'heure de fin doit etre apres l'heure de debut",
  path: ['heure_fin'],
})

export type ReservationFormData = z.infer<typeof reservationSchema>

// Schema de validation pour les pointages
export const pointageSchema = z.object({
  date: z.string().min(1, errorMessages.required),
  heure_debut: z
    .string()
    .regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Format heure invalide (HH:MM)'),
  heure_fin: z
    .string()
    .regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Format heure invalide (HH:MM)'),
  chantier_id: z
    .string()
    .min(1, 'Veuillez selectionner un chantier'),
  type_pointage: z.enum(['normal', 'heures_sup', 'nuit', 'weekend']),
  note: z
    .string()
    .max(500, errorMessages.maxLength(500))
    .optional(),
})

export type PointageFormData = z.infer<typeof pointageSchema>

// Schema de validation pour les commentaires/mentions
export const commentSchema = z.object({
  contenu: z
    .string()
    .min(1, 'Le commentaire ne peut pas etre vide')
    .max(2000, errorMessages.maxLength(2000)),
})

export type CommentFormData = z.infer<typeof commentSchema>

// Helper pour valider un formulaire avec Zod
export function validateForm<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: true; data: T } | { success: false; errors: Record<string, string> } {
  const result = schema.safeParse(data)

  if (result.success) {
    return { success: true, data: result.data }
  }

  const errors: Record<string, string> = {}
  for (const issue of result.error.issues) {
    const path = issue.path.join('.')
    if (!errors[path]) {
      errors[path] = issue.message
    }
  }

  return { success: false, errors }
}
