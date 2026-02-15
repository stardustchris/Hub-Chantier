"""Service de numerotation automatique des lots/chapitres/lignes.

DEV-03: Creation devis structure - Numerotation hierarchique automatique.

Genere des codes hierarchiques pour l'arborescence du devis:
  - Lots racine: 1, 2, 3...
  - Sous-chapitres: 1.1, 1.2, 2.1...
  - Sous-sous-chapitres: 1.1.1, 1.1.2...
  - Lignes: 1.1.01, 1.1.02... (sur 2 chiffres)
"""

from typing import List, Optional


class NumerotationService:
    """Service domain pour la numerotation automatique.

    Genere des codes hierarchiques pour les lots et lignes d'un devis.
    La numerotation est deterministe et basee sur l'ordre d'affichage.
    """

    @staticmethod
    def generer_code_lot(
        ordre: int,
        parent_code: Optional[str] = None,
    ) -> str:
        """Genere le code d'un lot dans l'arborescence.

        Args:
            ordre: Position du lot (0-based index dans la liste des freres).
            parent_code: Code du lot parent (None = lot racine).

        Returns:
            Le code hierarchique du lot (ex: "1", "1.2", "2.1.3").

        Examples:
            >>> NumerotationService.generer_code_lot(0)
            '1'
            >>> NumerotationService.generer_code_lot(2, parent_code="1")
            '1.3'
            >>> NumerotationService.generer_code_lot(0, parent_code="2.1")
            '2.1.1'
        """
        numero = str(ordre + 1)
        if parent_code:
            return f"{parent_code}.{numero}"
        return numero

    @staticmethod
    def generer_code_ligne(
        ordre: int,
        lot_code: str,
    ) -> str:
        """Genere le code d'une ligne dans un lot.

        Les lignes sont numerotees sur 2 chiffres (01, 02...).

        Args:
            ordre: Position de la ligne (0-based index).
            lot_code: Code du lot parent.

        Returns:
            Le code hierarchique de la ligne (ex: "1.01", "2.1.03").

        Examples:
            >>> NumerotationService.generer_code_ligne(0, "1")
            '1.01'
            >>> NumerotationService.generer_code_ligne(4, "2.1")
            '2.1.05'
        """
        numero_ligne = f"{ordre + 1:02d}"
        return f"{lot_code}.{numero_ligne}"

    @staticmethod
    def renumeroter_lots(
        lot_codes_parents: List[Optional[str]],
        ordres: List[int],
    ) -> List[str]:
        """Renumerote une liste de lots en batch.

        Utile apres un reordonnement par drag & drop.

        Args:
            lot_codes_parents: Code parent de chaque lot (None = racine).
            ordres: Nouvel ordre de chaque lot (0-based).

        Returns:
            Liste des nouveaux codes dans le meme ordre.

        Raises:
            ValueError: Si les listes n'ont pas la meme longueur.
        """
        if len(lot_codes_parents) != len(ordres):
            raise ValueError(
                "Les listes lot_codes_parents et ordres doivent avoir la meme longueur"
            )
        return [
            NumerotationService.generer_code_lot(ordre, parent)
            for parent, ordre in zip(lot_codes_parents, ordres)
        ]

    @staticmethod
    def renumeroter_lignes(
        lot_code: str,
        count: int,
    ) -> List[str]:
        """Genere les codes pour toutes les lignes d'un lot.

        Args:
            lot_code: Code du lot parent.
            count: Nombre de lignes.

        Returns:
            Liste des codes de lignes ordonnes.
        """
        return [
            NumerotationService.generer_code_ligne(i, lot_code)
            for i in range(count)
        ]
