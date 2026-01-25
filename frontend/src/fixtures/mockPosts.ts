/**
 * Mock posts pour démonstration du feed
 * IDs négatifs pour éviter conflits avec l'API
 */
import type { Post } from '../types'

export const MOCK_POSTS: Post[] = [
  {
    id: '-1',
    contenu: 'Dalle coulée avec succès sur le chantier Villa Moderne ! Beau travail de toute l\'équipe malgré la météo difficile ce matin.',
    type: 'message',
    auteur: { id: '1', prenom: 'Pierre', nom: 'Martin', couleur: '#3498DB', role: 'chef_chantier' } as Post['auteur'],
    target_type: 'tous',
    is_pinned: true,
    is_urgent: false,
    likes_count: 12,
    commentaires_count: 3,
    likes: [],
    medias: [],
    commentaires: [
      { id: 'c1', contenu: 'Bravo à tous !', auteur: { id: '2', prenom: 'Marie', nom: 'Dupont', couleur: '#E74C3C' } as Post['auteur'], created_at: new Date(Date.now() - 3600000).toISOString() },
      { id: 'c2', contenu: 'Excellent travail malgré la pluie !', auteur: { id: '5', prenom: 'Sophie', nom: 'Technique', couleur: '#F39C12' } as Post['auteur'], created_at: new Date(Date.now() - 3000000).toISOString() },
      { id: 'c3', contenu: 'On enchaîne demain avec le ferraillage', auteur: { id: '1', prenom: 'Pierre', nom: 'Martin', couleur: '#3498DB' } as Post['auteur'], created_at: new Date(Date.now() - 2400000).toISOString() },
    ],
    created_at: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    id: '-2',
    contenu: '⚠️ URGENT: Livraison de béton décalée à 14h au lieu de 10h sur Résidence Les Pins. Merci de réorganiser les équipes.',
    type: 'urgent',
    auteur: { id: '3', prenom: 'Jean', nom: 'Conducteur', couleur: '#9B59B6', role: 'conducteur' } as Post['auteur'],
    target_type: 'chantiers',
    target_chantiers: [{ id: 'ch1', nom: 'Résidence Les Pins' }] as Post['target_chantiers'],
    is_pinned: false,
    is_urgent: true,
    likes_count: 5,
    commentaires_count: 2,
    likes: [],
    medias: [],
    commentaires: [
      { id: 'c4', contenu: 'Bien reçu, je préviens l\'équipe', auteur: { id: '1', prenom: 'Pierre', nom: 'Martin', couleur: '#3498DB' } as Post['auteur'], created_at: new Date(Date.now() - 1500000).toISOString() },
      { id: 'c5', contenu: 'OK je décale le planning en conséquence', auteur: { id: '5', prenom: 'Sophie', nom: 'Technique', couleur: '#F39C12' } as Post['auteur'], created_at: new Date(Date.now() - 1200000).toISOString() },
    ],
    created_at: new Date(Date.now() - 1800000).toISOString(),
  },
  {
    id: '-3',
    contenu: 'Formation sécurité effectuée ce matin. Rappel: port du casque OBLIGATOIRE sur tous les chantiers. Bonne journée à tous !',
    type: 'message',
    auteur: { id: '4', prenom: 'Admin', nom: 'Greg', couleur: '#27AE60', role: 'admin' } as Post['auteur'],
    target_type: 'tous',
    is_pinned: false,
    is_urgent: false,
    likes_count: 24,
    commentaires_count: 2,
    likes: [],
    medias: [],
    commentaires: [
      { id: 'c6', contenu: 'Merci pour le rappel !', auteur: { id: '2', prenom: 'Marie', nom: 'Dupont', couleur: '#E74C3C' } as Post['auteur'], created_at: new Date(Date.now() - 80000000).toISOString() },
      { id: 'c7', contenu: 'Bien noté chef', auteur: { id: '1', prenom: 'Pierre', nom: 'Martin', couleur: '#3498DB' } as Post['auteur'], created_at: new Date(Date.now() - 75000000).toISOString() },
    ],
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: '-4',
    contenu: 'Nouvelle machine arrivée sur le chantier École Pasteur. Formation d\'utilisation demain à 8h pour les volontaires.',
    type: 'message',
    auteur: { id: '5', prenom: 'Sophie', nom: 'Technique', couleur: '#F39C12', role: 'chef_chantier' } as Post['auteur'],
    target_type: 'tous',
    is_pinned: false,
    is_urgent: false,
    likes_count: 8,
    commentaires_count: 3,
    likes: [],
    medias: [],
    commentaires: [
      { id: 'c8', contenu: 'Je serai là !', auteur: { id: '1', prenom: 'Pierre', nom: 'Martin', couleur: '#3498DB' } as Post['auteur'], created_at: new Date(Date.now() - 160000000).toISOString() },
      { id: 'c9', contenu: 'Moi aussi, ça m\'intéresse', auteur: { id: '2', prenom: 'Marie', nom: 'Dupont', couleur: '#E74C3C' } as Post['auteur'], created_at: new Date(Date.now() - 155000000).toISOString() },
      { id: 'c10', contenu: 'Super, rendez-vous à 8h devant le local', auteur: { id: '5', prenom: 'Sophie', nom: 'Technique', couleur: '#F39C12' } as Post['auteur'], created_at: new Date(Date.now() - 150000000).toISOString() },
    ],
    created_at: new Date(Date.now() - 172800000).toISOString(),
  },
  {
    id: '-5',
    contenu: 'Félicitations à l\'équipe du chantier Maison Durand pour la livraison en avance ! Client très satisfait.',
    type: 'message',
    auteur: { id: '4', prenom: 'Admin', nom: 'Greg', couleur: '#27AE60', role: 'admin' } as Post['auteur'],
    target_type: 'tous',
    is_pinned: false,
    is_urgent: false,
    likes_count: 45,
    commentaires_count: 2,
    likes: [],
    medias: [],
    commentaires: [
      { id: 'c11', contenu: 'Merci ! Toute l\'équipe a donné le maximum', auteur: { id: '1', prenom: 'Pierre', nom: 'Martin', couleur: '#3498DB' } as Post['auteur'], created_at: new Date(Date.now() - 250000000).toISOString() },
      { id: 'c12', contenu: 'Bravo à tous, bien mérité !', auteur: { id: '3', prenom: 'Jean', nom: 'Conducteur', couleur: '#9B59B6' } as Post['auteur'], created_at: new Date(Date.now() - 245000000).toISOString() },
    ],
    created_at: new Date(Date.now() - 259200000).toISOString(),
  },
]

/**
 * Helper pour détecter les posts mock (IDs négatifs)
 */
export function isMockPost(postId: string | number): boolean {
  const numId = typeof postId === 'string' ? parseInt(postId, 10) : postId
  return numId < 0 || isNaN(numId)
}
