/**
 * Schemas de validation Zod pour le frontend
 *
 * Tous les schemas de validation sont centralises ici pour:
 * - Coherence des regles de validation
 * - Reutilisation entre les formulaires
 * - Messages d'erreur en francais
 */

import { z } from 'zod'

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
  role: z.enum(['admin', 'conducteur', 'chef_chantier', 'compagnon']),
  metier: z
    .string()
    .max(100, errorMessages.maxLength(100))
    .optional(),
})

export type UserFormData = z.infer<typeof userSchema>

// Schema de validation pour les chantiers
export const chantierSchema = z.object({
  nom: z
    .string()
    .min(1, errorMessages.required)
    .max(100, errorMessages.maxLength(100)),
  code: z
    .string()
    .min(1, errorMessages.required)
    .max(20, errorMessages.maxLength(20))
    .regex(/^[A-Z0-9-]+$/, 'Le code doit contenir uniquement des lettres majuscules, chiffres et tirets'),
  adresse: z
    .string()
    .min(1, errorMessages.required)
    .max(200, errorMessages.maxLength(200)),
  ville: z
    .string()
    .min(1, errorMessages.required)
    .max(100, errorMessages.maxLength(100)),
  code_postal: z
    .string()
    .regex(/^\d{5}$/, 'Le code postal doit contenir 5 chiffres'),
  date_debut: z.string().min(1, errorMessages.required),
  date_fin_prevue: z.string().optional(),
  budget: z
    .number()
    .positive(errorMessages.positive)
    .optional(),
  client_nom: z
    .string()
    .max(100, errorMessages.maxLength(100))
    .optional(),
})

export type ChantierFormData = z.infer<typeof chantierSchema>

// Schema de validation pour les reservations
export const reservationSchema = z.object({
  ressource_id: z
    .string()
    .min(1, 'Veuillez selectionner une ressource'),
  chantier_id: z
    .string()
    .min(1, 'Veuillez selectionner un chantier'),
  date_debut: z.string().min(1, errorMessages.required),
  date_fin: z.string().min(1, errorMessages.required),
  quantite: z
    .number()
    .min(1, 'La quantite doit etre au moins 1')
    .optional()
    .default(1),
  note: z
    .string()
    .max(500, errorMessages.maxLength(500))
    .optional(),
}).refine((data) => new Date(data.date_fin) >= new Date(data.date_debut), {
  message: 'La date de fin doit etre apres la date de debut',
  path: ['date_fin'],
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
