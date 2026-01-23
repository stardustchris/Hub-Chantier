"""Tests des Value Objects du module Documents."""

import pytest

from modules.documents.domain.value_objects import (
    NiveauAcces,
    TypeDocument,
    DossierType,
)


class TestNiveauAcces:
    """Tests pour NiveauAcces."""

    def test_niveaux_disponibles(self):
        """Verifie que les niveaux d'acces sont disponibles."""
        assert NiveauAcces.COMPAGNON.value == "compagnon"
        assert NiveauAcces.CHEF_CHANTIER.value == "chef_chantier"
        assert NiveauAcces.CONDUCTEUR.value == "conducteur"
        assert NiveauAcces.ADMIN.value == "admin"

    def test_ordre_hierarchique(self):
        """Verifie l'ordre hierarchique des niveaux."""
        assert NiveauAcces.COMPAGNON.ordre == 1
        assert NiveauAcces.CHEF_CHANTIER.ordre == 2
        assert NiveauAcces.CONDUCTEUR.ordre == 3
        assert NiveauAcces.ADMIN.ordre == 4

    def test_description(self):
        """Verifie les descriptions des niveaux."""
        assert "Tous les utilisateurs" in NiveauAcces.COMPAGNON.description
        assert "Chefs de chantier" in NiveauAcces.CHEF_CHANTIER.description
        assert "Conducteurs" in NiveauAcces.CONDUCTEUR.description
        assert "Administrateurs" in NiveauAcces.ADMIN.description

    def test_peut_acceder_admin(self):
        """Verifie qu'un admin peut acceder a tous les niveaux."""
        assert NiveauAcces.COMPAGNON.peut_acceder("admin") is True
        assert NiveauAcces.CHEF_CHANTIER.peut_acceder("admin") is True
        assert NiveauAcces.CONDUCTEUR.peut_acceder("admin") is True
        assert NiveauAcces.ADMIN.peut_acceder("admin") is True

    def test_peut_acceder_conducteur(self):
        """Verifie qu'un conducteur peut acceder jusqu'au niveau conducteur."""
        assert NiveauAcces.COMPAGNON.peut_acceder("conducteur") is True
        assert NiveauAcces.CHEF_CHANTIER.peut_acceder("conducteur") is True
        assert NiveauAcces.CONDUCTEUR.peut_acceder("conducteur") is True
        assert NiveauAcces.ADMIN.peut_acceder("conducteur") is False

    def test_peut_acceder_chef_chantier(self):
        """Verifie qu'un chef de chantier peut acceder jusqu'au niveau chef."""
        assert NiveauAcces.COMPAGNON.peut_acceder("chef_chantier") is True
        assert NiveauAcces.CHEF_CHANTIER.peut_acceder("chef_chantier") is True
        assert NiveauAcces.CONDUCTEUR.peut_acceder("chef_chantier") is False
        assert NiveauAcces.ADMIN.peut_acceder("chef_chantier") is False

    def test_peut_acceder_compagnon(self):
        """Verifie qu'un compagnon ne peut acceder qu'au niveau compagnon."""
        assert NiveauAcces.COMPAGNON.peut_acceder("compagnon") is True
        assert NiveauAcces.CHEF_CHANTIER.peut_acceder("compagnon") is False
        assert NiveauAcces.CONDUCTEUR.peut_acceder("compagnon") is False
        assert NiveauAcces.ADMIN.peut_acceder("compagnon") is False

    def test_peut_acceder_role_alias(self):
        """Verifie les alias de roles."""
        assert NiveauAcces.ADMIN.peut_acceder("administrateur") is True
        assert NiveauAcces.CHEF_CHANTIER.peut_acceder("chef") is True

    def test_peut_acceder_role_invalide(self):
        """Verifie qu'un role invalide n'a pas acces."""
        assert NiveauAcces.COMPAGNON.peut_acceder("invalid_role") is False

    def test_from_string(self):
        """Verifie la conversion depuis string."""
        assert NiveauAcces.from_string("compagnon") == NiveauAcces.COMPAGNON
        assert NiveauAcces.from_string("ADMIN") == NiveauAcces.ADMIN
        assert NiveauAcces.from_string("Chef_Chantier") == NiveauAcces.CHEF_CHANTIER

    def test_from_string_invalid(self):
        """Verifie l'erreur pour niveau invalide."""
        with pytest.raises(ValueError, match="invalide"):
            NiveauAcces.from_string("invalid_niveau")

    def test_list_all(self):
        """Verifie la liste de tous les niveaux."""
        niveaux = NiveauAcces.list_all()
        assert len(niveaux) == 4
        assert any(n["value"] == "compagnon" for n in niveaux)
        assert any(n["value"] == "admin" for n in niveaux)
        assert all("description" in n and "ordre" in n for n in niveaux)


class TestTypeDocument:
    """Tests pour TypeDocument."""

    def test_types_disponibles(self):
        """Verifie que les types de documents sont disponibles."""
        assert TypeDocument.PDF.value == "pdf"
        assert TypeDocument.IMAGE.value == "image"
        assert TypeDocument.EXCEL.value == "excel"
        assert TypeDocument.WORD.value == "word"
        assert TypeDocument.VIDEO.value == "video"
        assert TypeDocument.AUTRE.value == "autre"

    def test_extensions_pdf(self):
        """Verifie les extensions PDF."""
        assert ".pdf" in TypeDocument.PDF.extensions

    def test_extensions_image(self):
        """Verifie les extensions image."""
        extensions = TypeDocument.IMAGE.extensions
        assert ".png" in extensions
        assert ".jpg" in extensions
        assert ".jpeg" in extensions
        assert ".gif" in extensions
        assert ".webp" in extensions

    def test_extensions_excel(self):
        """Verifie les extensions Excel."""
        extensions = TypeDocument.EXCEL.extensions
        assert ".xls" in extensions
        assert ".xlsx" in extensions
        assert ".csv" in extensions

    def test_extensions_word(self):
        """Verifie les extensions Word."""
        extensions = TypeDocument.WORD.extensions
        assert ".doc" in extensions
        assert ".docx" in extensions
        assert ".odt" in extensions

    def test_extensions_video(self):
        """Verifie les extensions video."""
        extensions = TypeDocument.VIDEO.extensions
        assert ".mp4" in extensions
        assert ".avi" in extensions
        assert ".mov" in extensions

    def test_mime_types_pdf(self):
        """Verifie les types MIME PDF."""
        assert "application/pdf" in TypeDocument.PDF.mime_types

    def test_mime_types_image(self):
        """Verifie les types MIME image."""
        mime_types = TypeDocument.IMAGE.mime_types
        assert "image/png" in mime_types
        assert "image/jpeg" in mime_types

    def test_icones(self):
        """Verifie les icones associees."""
        assert TypeDocument.PDF.icone == "file-pdf"
        assert TypeDocument.IMAGE.icone == "file-image"
        assert TypeDocument.EXCEL.icone == "file-excel"
        assert TypeDocument.WORD.icone == "file-word"
        assert TypeDocument.VIDEO.icone == "file-video"
        assert TypeDocument.AUTRE.icone == "file"

    def test_from_extension_pdf(self):
        """Verifie la detection du type PDF."""
        assert TypeDocument.from_extension(".pdf") == TypeDocument.PDF
        assert TypeDocument.from_extension("pdf") == TypeDocument.PDF

    def test_from_extension_image(self):
        """Verifie la detection du type image."""
        assert TypeDocument.from_extension(".png") == TypeDocument.IMAGE
        assert TypeDocument.from_extension("jpg") == TypeDocument.IMAGE
        assert TypeDocument.from_extension(".jpeg") == TypeDocument.IMAGE

    def test_from_extension_excel(self):
        """Verifie la detection du type Excel."""
        assert TypeDocument.from_extension(".xlsx") == TypeDocument.EXCEL
        assert TypeDocument.from_extension("xls") == TypeDocument.EXCEL
        assert TypeDocument.from_extension(".csv") == TypeDocument.EXCEL

    def test_from_extension_word(self):
        """Verifie la detection du type Word."""
        assert TypeDocument.from_extension(".docx") == TypeDocument.WORD
        assert TypeDocument.from_extension("doc") == TypeDocument.WORD

    def test_from_extension_video(self):
        """Verifie la detection du type video."""
        assert TypeDocument.from_extension(".mp4") == TypeDocument.VIDEO
        assert TypeDocument.from_extension("avi") == TypeDocument.VIDEO

    def test_from_extension_inconnu(self):
        """Verifie le type AUTRE pour extension inconnue."""
        assert TypeDocument.from_extension(".xyz") == TypeDocument.AUTRE
        assert TypeDocument.from_extension("unknown") == TypeDocument.AUTRE

    def test_from_mime_type_pdf(self):
        """Verifie la detection depuis type MIME PDF."""
        assert TypeDocument.from_mime_type("application/pdf") == TypeDocument.PDF

    def test_from_mime_type_image(self):
        """Verifie la detection depuis type MIME image."""
        assert TypeDocument.from_mime_type("image/png") == TypeDocument.IMAGE
        assert TypeDocument.from_mime_type("image/jpeg") == TypeDocument.IMAGE

    def test_from_mime_type_inconnu(self):
        """Verifie le type AUTRE pour MIME inconnu."""
        assert TypeDocument.from_mime_type("application/unknown") == TypeDocument.AUTRE

    def test_list_extensions_acceptees(self):
        """Verifie la liste des extensions acceptees."""
        extensions = TypeDocument.list_extensions_acceptees()
        assert ".pdf" in extensions
        assert ".png" in extensions
        assert ".xlsx" in extensions
        assert ".mp4" in extensions
        # AUTRE n'a pas d'extensions
        assert len([e for e in extensions if e == ""]) == 0


class TestDossierType:
    """Tests pour DossierType."""

    def test_types_disponibles(self):
        """Verifie que les types de dossiers sont disponibles."""
        assert DossierType.PLANS.value == "01_plans"
        assert DossierType.ADMINISTRATIF.value == "02_administratif"
        assert DossierType.SECURITE.value == "03_securite"
        assert DossierType.QUALITE.value == "04_qualite"
        assert DossierType.PHOTOS.value == "05_photos"
        assert DossierType.COMPTES_RENDUS.value == "06_comptes_rendus"
        assert DossierType.LIVRAISONS.value == "07_livraisons"
        assert DossierType.CUSTOM.value == "custom"

    def test_numero(self):
        """Verifie les numeros de dossiers."""
        assert DossierType.PLANS.numero == "01"
        assert DossierType.ADMINISTRATIF.numero == "02"
        assert DossierType.SECURITE.numero == "03"
        assert DossierType.CUSTOM.numero == "99"

    def test_nom_affichage(self):
        """Verifie les noms d'affichage."""
        assert DossierType.PLANS.nom_affichage == "Plans"
        assert DossierType.ADMINISTRATIF.nom_affichage == "Documents administratifs"
        assert DossierType.SECURITE.nom_affichage == "Sécurité"
        assert DossierType.CUSTOM.nom_affichage == "Personnalisé"

    def test_description(self):
        """Verifie les descriptions."""
        assert "Plans d'exécution" in DossierType.PLANS.description
        assert "Marchés" in DossierType.ADMINISTRATIF.description
        assert "PPSPS" in DossierType.SECURITE.description
        assert "Fiches techniques" in DossierType.QUALITE.description
        assert "Photos chantier" in DossierType.PHOTOS.description
        assert "CR réunions" in DossierType.COMPTES_RENDUS.description
        assert "Bons de livraison" in DossierType.LIVRAISONS.description

    def test_niveau_acces_defaut(self):
        """Verifie les niveaux d'acces par defaut."""
        assert DossierType.PLANS.niveau_acces_defaut == "compagnon"
        assert DossierType.ADMINISTRATIF.niveau_acces_defaut == "conducteur"
        assert DossierType.SECURITE.niveau_acces_defaut == "compagnon"
        assert DossierType.QUALITE.niveau_acces_defaut == "chef_chantier"
        assert DossierType.PHOTOS.niveau_acces_defaut == "compagnon"
        assert DossierType.COMPTES_RENDUS.niveau_acces_defaut == "chef_chantier"
        assert DossierType.LIVRAISONS.niveau_acces_defaut == "chef_chantier"
        assert DossierType.CUSTOM.niveau_acces_defaut == "chef_chantier"

    def test_from_string_valide(self):
        """Verifie la conversion depuis string valide."""
        assert DossierType.from_string("01_plans") == DossierType.PLANS
        assert DossierType.from_string("02_administratif") == DossierType.ADMINISTRATIF
        assert DossierType.from_string("custom") == DossierType.CUSTOM

    def test_from_string_par_nom_affichage(self):
        """Verifie la conversion depuis nom d'affichage."""
        assert DossierType.from_string("Plans") == DossierType.PLANS
        assert DossierType.from_string("Sécurité") == DossierType.SECURITE

    def test_from_string_inconnu_retourne_custom(self):
        """Verifie que les valeurs inconnues retournent CUSTOM."""
        assert DossierType.from_string("dossier_inconnu") == DossierType.CUSTOM

    def test_list_all(self):
        """Verifie la liste de tous les types (sans CUSTOM)."""
        types = DossierType.list_all()
        # CUSTOM n'est pas inclus
        assert len(types) == 7
        assert all("value" in t for t in types)
        assert all("numero" in t for t in types)
        assert all("nom" in t for t in types)
        assert all("description" in t for t in types)
        assert all("niveau_acces_defaut" in t for t in types)
        # Verifier que CUSTOM n'est pas dans la liste
        assert not any(t["value"] == "custom" for t in types)
