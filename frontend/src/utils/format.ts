/**
 * Utilitaires de formatage financier centralisés.
 * Locale fr-FR pour tous les montants et pourcentages.
 */

const eurFormatter = new Intl.NumberFormat('fr-FR', {
  style: 'currency',
  currency: 'EUR',
})

const pctFormatter = (decimals: number) =>
  new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })

export const formatEUR = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined) return '\u2014'  // tiret cadratin (—) pour "non renseigné"
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '\u2014'
  return eurFormatter.format(num)
}

export const formatPct = (value: number | string | null | undefined, decimals = 1): string => {
  if (value === null || value === undefined) return '\u2014'  // tiret cadratin (—) pour "non renseigné"
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '\u2014'
  return pctFormatter(decimals).format(num) + ' %'
}

/**
 * Libelles des echeances de paiement.
 * Deux formats de valeurs coexistent en base : celui du formulaire devis
 * ('reception', '30_jours_fin_mois') et celui des donnees existantes ('30j_reception').
 * Les deux sont couverts pour ne jamais afficher de valeur technique au client.
 */
const ECHEANCE_LABELS: Record<string, string> = {
  reception: 'Paiement a reception',
  '30j_reception': '30 jours a reception',
  '30j_facture': '30 jours date de facture',
  '30j_fin_mois': '30 jours fin de mois',
  '30_jours_fin_mois': '30 jours fin de mois',
  '45j_fin_mois': '45 jours fin de mois',
  '45_jours_fin_mois': '45 jours fin de mois',
  '60j': '60 jours',
  '60_jours': '60 jours',
}

export const formatEcheance = (value: string | null | undefined): string => {
  if (!value) return '—'
  return ECHEANCE_LABELS[value] ?? value.replace(/_/g, ' ')
}
