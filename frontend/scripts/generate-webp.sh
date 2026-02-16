#!/bin/bash

# Script de génération d'images WebP pour Hub Chantier
# Nécessite ImageMagick ou cwebp (Google WebP tools)

set -e

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Dossier public
PUBLIC_DIR="$(dirname "$0")/../public"

echo -e "${GREEN}🖼️  Génération d'images WebP pour Hub Chantier${NC}"
echo "---"

# Vérifier si cwebp est installé
if command -v cwebp &> /dev/null; then
    CONVERTER="cwebp"
    echo -e "${GREEN}✓${NC} cwebp trouvé (Google WebP tools)"
elif command -v convert &> /dev/null; then
    CONVERTER="convert"
    echo -e "${GREEN}✓${NC} ImageMagick trouvé"
else
    echo -e "${RED}✗${NC} Aucun convertisseur trouvé!"
    echo ""
    echo "Installez l'un des outils suivants:"
    echo ""
    echo "  Ubuntu/Debian:"
    echo "    sudo apt-get install webp"
    echo "    # ou"
    echo "    sudo apt-get install imagemagick"
    echo ""
    echo "  macOS:"
    echo "    brew install webp"
    echo "    # ou"
    echo "    brew install imagemagick"
    echo ""
    exit 1
fi

echo ""

# Fonction de conversion
convert_to_webp() {
    local input="$1"
    local output="$2"
    local quality="${3:-85}"

    if [ ! -f "$input" ]; then
        echo -e "${YELLOW}⚠${NC}  Fichier non trouvé: $input"
        return 1
    fi

    local input_size=$(du -h "$input" | cut -f1)

    if [ "$CONVERTER" = "cwebp" ]; then
        cwebp -q $quality "$input" -o "$output" 2>/dev/null
    else
        convert "$input" -quality $quality "$output"
    fi

    if [ -f "$output" ]; then
        local output_size=$(du -h "$output" | cut -f1)
        local reduction=$(echo "scale=1; (1 - $(stat -f%z "$output") / $(stat -f%z "$input")) * 100" | bc 2>/dev/null || echo "?")
        echo -e "${GREEN}✓${NC} $(basename "$input") → $(basename "$output")"
        echo "   $input_size → $output_size (${reduction}% réduction)"
        return 0
    else
        echo -e "${RED}✗${NC} Échec de conversion: $input"
        return 1
    fi
}

# Convertir le logo principal
echo "Conversion du logo principal..."
convert_to_webp "$PUBLIC_DIR/logo.png" "$PUBLIC_DIR/logo.webp" 85

echo ""

# Convertir les icônes PWA
echo "Conversion des icônes PWA..."
if [ -f "$PUBLIC_DIR/pwa-192x192.png" ]; then
    convert_to_webp "$PUBLIC_DIR/pwa-192x192.png" "$PUBLIC_DIR/pwa-192x192.webp" 90
fi

if [ -f "$PUBLIC_DIR/pwa-512x512.png" ]; then
    convert_to_webp "$PUBLIC_DIR/pwa-512x512.png" "$PUBLIC_DIR/pwa-512x512.webp" 90
fi

echo ""

# Convertir apple-touch-icon si présent
if [ -f "$PUBLIC_DIR/apple-touch-icon.png" ]; then
    echo "Conversion de apple-touch-icon..."
    convert_to_webp "$PUBLIC_DIR/apple-touch-icon.png" "$PUBLIC_DIR/apple-touch-icon.webp" 90
    echo ""
fi

# Récapitulatif
echo -e "${GREEN}✓ Génération terminée!${NC}"
echo ""
echo "Fichiers WebP créés dans: $PUBLIC_DIR"
echo ""
echo "⚠️  Note: Les icônes PWA WebP sont générées mais iOS ne les supporte pas."
echo "   Les fichiers PNG originaux doivent être conservés."
echo ""
echo "Prochaine étape: Vider le cache navigateur (Ctrl+Shift+R) pour voir les changements."
