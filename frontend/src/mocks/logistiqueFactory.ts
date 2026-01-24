/**
 * Factory pour generer des donnees de test du module Logistique.
 * Donnees dynamiques, pas de valeurs en dur.
 */

import type {
  Ressource,
  Reservation,
  CategorieRessource,
  StatutReservation,
} from '../types/logistique'
import { CATEGORIES_RESSOURCES, STATUTS_RESERVATION } from '../types/logistique'

// Pools de donnees pour generation aleatoire
const NOMS_PAR_CATEGORIE: Record<CategorieRessource, string[]> = {
  engin_levage: [
    'Grue mobile',
    'Grue a tour',
    'Nacelle elevatrice',
    'Chariot elevateur',
    'Mini-grue araignee',
    'Palan electrique',
  ],
  engin_terrassement: [
    'Mini-pelle',
    'Pelleteuse',
    'Compacteur',
    'Dumper',
    'Bulldozer',
    'Tractopelle',
  ],
  vehicule: [
    'Camion-benne',
    'Camionnette utilitaire',
    'Fourgon',
    'Camion plateau',
    'Tracteur agricole',
    '4x4 chantier',
  ],
  gros_outillage: [
    'Marteau-piqueur',
    'Groupe electrogene',
    'Compresseur',
    'Betonniere',
    'Poste a souder MIG',
    'Disqueuse',
  ],
  equipement: [
    'Echafaudage roulant',
    'Etais telescopiques',
    'Banches coffrage',
    'Barriere de chantier',
    'Benne a beton',
    'Coffrage modulaire',
  ],
}

const COULEURS = [
  '#FF5733',
  '#3498DB',
  '#27AE60',
  '#9B59B6',
  '#E74C3C',
  '#1ABC9C',
  '#F39C12',
  '#2ECC71',
  '#E67E22',
  '#8E44AD',
]

const COMMENTAIRES = [
  'Besoin pour travaux de fondation',
  'Utilisation prevue toute la journee',
  'Chantier prioritaire - livraison beton',
  'Installation echafaudage prevu',
  'Travaux de finition interieure',
  'Demontage structure metallique',
  'Coulage dalle',
  'Pose menuiseries exterieures',
  'Travaux toiture - etancheite',
  'Installation reseau electrique',
]

const CATEGORIES: CategorieRessource[] = [
  'engin_levage',
  'engin_terrassement',
  'vehicule',
  'gros_outillage',
  'equipement',
]

// Utilitaires
function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

function randomChoice<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)]
}

function randomCode(prefix: string): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  const suffix = Array.from({ length: 4 }, () =>
    chars.charAt(Math.floor(Math.random() * chars.length))
  ).join('')
  return `${prefix}${suffix}`
}

function formatDate(date: Date): string {
  return date.toISOString().split('T')[0]
}

function formatTime(hours: number, minutes: number = 0): string {
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
}

let ressourceCounter = 0
let reservationCounter = 0

/**
 * Factory pour creer des ressources de test
 */
export const RessourceFactory = {
  /**
   * Remet le compteur a zero
   */
  resetCounter() {
    ressourceCounter = 0
  },

  /**
   * Cree une ressource avec des valeurs aleatoires
   */
  create(overrides: Partial<Ressource> = {}): Ressource {
    ressourceCounter++
    const id = overrides.id ?? ressourceCounter
    const categorie = overrides.categorie ?? randomChoice(CATEGORIES)
    const noms = NOMS_PAR_CATEGORIE[categorie]
    const baseName = randomChoice(noms)
    const suffix = randomInt(10, 100)
    const categorieInfo = CATEGORIES_RESSOURCES[categorie]

    const now = new Date().toISOString()

    return {
      id,
      code: overrides.code ?? randomCode(categorie.substring(0, 3).toUpperCase()),
      nom: overrides.nom ?? `${baseName} ${suffix}`,
      description: overrides.description ?? `Ressource de type ${categorie}`,
      categorie,
      categorie_label: categorieInfo.label,
      couleur: overrides.couleur ?? randomChoice(COULEURS),
      photo_url: overrides.photo_url,
      heure_debut_defaut: overrides.heure_debut_defaut ?? formatTime(randomChoice([7, 8])),
      heure_fin_defaut: overrides.heure_fin_defaut ?? formatTime(randomChoice([17, 18])),
      validation_requise: overrides.validation_requise ?? categorieInfo.validationRequise,
      actif: overrides.actif ?? true,
      created_at: overrides.created_at ?? now,
      updated_at: overrides.updated_at ?? now,
    }
  },

  /**
   * Cree plusieurs ressources
   */
  createBatch(count: number, overrides: Partial<Ressource> = {}): Ressource[] {
    return Array.from({ length: count }, () => this.create(overrides))
  },

  /**
   * Cree une ressource par categorie
   */
  createOnePerCategory(): Ressource[] {
    return CATEGORIES.map((categorie) => this.create({ categorie }))
  },
}

/**
 * Factory pour creer des reservations de test
 */
export const ReservationFactory = {
  /**
   * Remet le compteur a zero
   */
  resetCounter() {
    reservationCounter = 0
  },

  /**
   * Cree une reservation avec des valeurs aleatoires
   */
  create(overrides: Partial<Reservation> = {}): Reservation {
    reservationCounter++
    const id = overrides.id ?? reservationCounter

    // Date aleatoire dans les 30 prochains jours
    const today = new Date()
    const daysOffset = randomInt(1, 30)
    const reservationDate = new Date(today)
    reservationDate.setDate(today.getDate() + daysOffset)

    // Plage horaire aleatoire
    const heureDebut = randomChoice([7, 8, 9, 10, 13, 14])
    const duree = randomChoice([2, 3, 4, 5])
    const heureFin = Math.min(heureDebut + duree, 19)

    const statut = overrides.statut ?? 'en_attente'
    const statutInfo = STATUTS_RESERVATION[statut]
    const now = new Date().toISOString()

    return {
      id,
      ressource_id: overrides.ressource_id ?? 1,
      ressource_nom: overrides.ressource_nom,
      ressource_code: overrides.ressource_code,
      ressource_couleur: overrides.ressource_couleur,
      chantier_id: overrides.chantier_id ?? randomInt(1, 10),
      chantier_nom: overrides.chantier_nom,
      demandeur_id: overrides.demandeur_id ?? randomInt(1, 20),
      demandeur_nom: overrides.demandeur_nom,
      date_reservation: overrides.date_reservation ?? formatDate(reservationDate),
      heure_debut: overrides.heure_debut ?? formatTime(heureDebut),
      heure_fin: overrides.heure_fin ?? formatTime(heureFin),
      statut,
      statut_label: statutInfo.label,
      statut_couleur: statutInfo.color,
      commentaire: overrides.commentaire ?? randomChoice(COMMENTAIRES),
      valideur_id:
        overrides.valideur_id ??
        (['validee', 'refusee'].includes(statut) ? randomInt(1, 5) : undefined),
      valideur_nom: overrides.valideur_nom,
      motif_refus:
        overrides.motif_refus ?? (statut === 'refusee' ? 'Ressource indisponible' : undefined),
      validated_at:
        overrides.validated_at ?? (['validee', 'refusee'].includes(statut) ? now : undefined),
      created_at: overrides.created_at ?? now,
      updated_at: overrides.updated_at ?? now,
    }
  },

  /**
   * Cree une reservation en attente
   */
  createEnAttente(overrides: Partial<Reservation> = {}): Reservation {
    return this.create({ ...overrides, statut: 'en_attente', valideur_id: undefined })
  },

  /**
   * Cree une reservation validee
   */
  createValidee(overrides: Partial<Reservation> = {}): Reservation {
    return this.create({
      ...overrides,
      statut: 'validee',
      valideur_id: overrides.valideur_id ?? 5,
      validated_at: overrides.validated_at ?? new Date().toISOString(),
    })
  },

  /**
   * Cree une reservation refusee
   */
  createRefusee(overrides: Partial<Reservation> = {}): Reservation {
    return this.create({
      ...overrides,
      statut: 'refusee',
      valideur_id: overrides.valideur_id ?? 5,
      motif_refus: overrides.motif_refus ?? 'Ressource indisponible',
      validated_at: overrides.validated_at ?? new Date().toISOString(),
    })
  },

  /**
   * Cree plusieurs reservations
   */
  createBatch(count: number, overrides: Partial<Reservation> = {}): Reservation[] {
    return Array.from({ length: count }, () => this.create(overrides))
  },

  /**
   * Cree un planning de reservations sur une semaine
   */
  createWeekPlanning(
    ressourceId: number,
    startDate?: Date,
    reservationsPerDay = 2
  ): Reservation[] {
    const today = startDate ?? new Date()
    // Trouver le lundi de la semaine
    const monday = new Date(today)
    monday.setDate(today.getDate() - today.getDay() + 1)

    const reservations: Reservation[] = []
    const statuts: StatutReservation[] = ['validee', 'validee', 'en_attente', 'refusee']

    for (let day = 0; day < 5; day++) {
      const currentDate = new Date(monday)
      currentDate.setDate(monday.getDate() + day)

      for (let slot = 0; slot < reservationsPerDay; slot++) {
        const heureDebut = slot === 0 ? '08:00' : '14:00'
        const heureFin = slot === 0 ? '12:00' : '17:00'

        reservations.push(
          this.create({
            ressource_id: ressourceId,
            date_reservation: formatDate(currentDate),
            heure_debut: heureDebut,
            heure_fin: heureFin,
            statut: randomChoice(statuts),
            chantier_id: randomInt(1, 5),
            demandeur_id: randomInt(10, 15),
          })
        )
      }
    }

    return reservations
  },
}

/**
 * Factory principale pour generer un jeu de donnees complet
 */
export const LogistiqueDataFactory = {
  /**
   * Cree un jeu de donnees complet
   */
  createFullDataset(
    ressourcesCount = 10,
    reservationsPerRessource = 5
  ): {
    ressources: Ressource[]
    reservations: Reservation[]
  } {
    RessourceFactory.resetCounter()
    ReservationFactory.resetCounter()

    const ressources = RessourceFactory.createBatch(ressourcesCount)
    const reservations: Reservation[] = []

    for (const ressource of ressources) {
      const ressourceReservations = ReservationFactory.createBatch(
        reservationsPerRessource,
        {
          ressource_id: ressource.id,
          ressource_nom: ressource.nom,
          ressource_code: ressource.code,
          ressource_couleur: ressource.couleur,
        }
      )
      reservations.push(...ressourceReservations)
    }

    return { ressources, reservations }
  },

  /**
   * Cree un jeu de donnees de demonstration
   */
  createDemoDataset(): {
    ressources: Ressource[]
    reservations: Reservation[]
  } {
    RessourceFactory.resetCounter()
    ReservationFactory.resetCounter()

    const ressources = RessourceFactory.createOnePerCategory()
    const reservations: Reservation[] = []

    for (const ressource of ressources) {
      const weekReservations = ReservationFactory.createWeekPlanning(ressource.id)
      // Enrichir avec les infos ressource
      weekReservations.forEach((r) => {
        r.ressource_nom = ressource.nom
        r.ressource_code = ressource.code
        r.ressource_couleur = ressource.couleur
      })
      reservations.push(...weekReservations)
    }

    return { ressources, reservations }
  },

  /**
   * Remet tous les compteurs a zero
   */
  resetCounters() {
    RessourceFactory.resetCounter()
    ReservationFactory.resetCounter()
  },
}
