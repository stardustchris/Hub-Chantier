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
