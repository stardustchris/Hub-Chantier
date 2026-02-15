/**
 * Composant image responsive avec support WebP srcset (P2-5).
 *
 * Utilise <picture> avec <source> WebP quand les variantes backend sont disponibles.
 * Fallback transparent sur <img> standard si pas de variantes.
 */

interface WebpVariants {
  webp_thumbnail_url?: string
  webp_medium_url?: string
  webp_large_url?: string
}

interface ResponsiveImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string
  alt: string
  webpVariants?: WebpVariants
}

export function ResponsiveImage({
  src,
  alt,
  webpVariants,
  ...imgProps
}: ResponsiveImageProps) {
  const hasWebp =
    webpVariants?.webp_thumbnail_url ||
    webpVariants?.webp_medium_url ||
    webpVariants?.webp_large_url

  if (!hasWebp) {
    return <img src={src} alt={alt} loading="lazy" decoding="async" {...imgProps} />
  }

  // Build srcset from available variants
  const srcsetParts: string[] = []
  if (webpVariants?.webp_thumbnail_url) {
    srcsetParts.push(`${webpVariants.webp_thumbnail_url} 300w`)
  }
  if (webpVariants?.webp_medium_url) {
    srcsetParts.push(`${webpVariants.webp_medium_url} 800w`)
  }
  if (webpVariants?.webp_large_url) {
    srcsetParts.push(`${webpVariants.webp_large_url} 1200w`)
  }

  return (
    <picture>
      <source
        type="image/webp"
        srcSet={srcsetParts.join(', ')}
        sizes="(max-width: 640px) 300px, (max-width: 1024px) 800px, 1200px"
      />
      <img src={src} alt={alt} loading="lazy" decoding="async" {...imgProps} />
    </picture>
  )
}
