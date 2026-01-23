"""Tests des Entites du module Documents."""

import pytest
from datetime import datetime, timedelta

from modules.documents.domain.entities import (
    Document,
    Dossier,
    AutorisationDocument,
    TypeAutorisation,
)
from modules.documents.domain.value_objects import (
    NiveauAcces,
    TypeDocument,
    DossierType,
)
from modules.documents.domain.entities.document import MAX_TAILLE_FICHIER


class TestDocument:
    """Tests pour Document."""

    def test_create_document_minimal(self):
        """Creation d'un document avec donnees minimales."""
        document = Document(
            chantier_id=1,
            dossier_id=1,
            nom="rapport.pdf",
            nom_original="rapport.pdf",
            chemin_stockage="/storage/rapport.pdf",
            taille=1024,
            mime_type="application/pdf",
            uploaded_by=1,
        )
        assert document.chantier_id == 1
        assert document.dossier_id == 1
        assert document.nom == "rapport.pdf"
        assert document.taille == 1024
        assert document.version == 1
        assert document.type_document == TypeDocument.PDF

    def test_create_document_complet(self):
        """Creation d'un document avec toutes les donnees."""
        document = Document(
            chantier_id=1,
            dossier_id=1,
            nom="plan.png",
            nom_original="plan_v2.png",
            chemin_stockage="/storage/plan.png",
            taille=2048000,
            mime_type="image/png",
            uploaded_by=1,
            type_document=TypeDocument.IMAGE,
            niveau_acces=NiveauAcces.CONDUCTEUR,
            description="Plan du rez-de-chaussee",
            version=2,
        )
        assert document.type_document == TypeDocument.IMAGE
        assert document.niveau_acces == NiveauAcces.CONDUCTEUR
        assert document.description == "Plan du rez-de-chaussee"
        assert document.version == 2

    def test_nom_vide_raise_error(self):
        """Verifie l'erreur pour nom vide."""
        with pytest.raises(ValueError, match="nom du document"):
            Document(
                chantier_id=1,
                dossier_id=1,
                nom="",
                nom_original="test.pdf",
                chemin_stockage="/storage/test.pdf",
                taille=1024,
                mime_type="application/pdf",
                uploaded_by=1,
            )

    def test_nom_espaces_raise_error(self):
        """Verifie l'erreur pour nom avec espaces uniquement."""
        with pytest.raises(ValueError, match="nom du document"):
            Document(
                chantier_id=1,
                dossier_id=1,
                nom="   ",
                nom_original="test.pdf",
                chemin_stockage="/storage/test.pdf",
                taille=1024,
                mime_type="application/pdf",
                uploaded_by=1,
            )

    def test_taille_negative_raise_error(self):
        """Verifie l'erreur pour taille negative."""
        with pytest.raises(ValueError, match="taille"):
            Document(
                chantier_id=1,
                dossier_id=1,
                nom="test.pdf",
                nom_original="test.pdf",
                chemin_stockage="/storage/test.pdf",
                taille=-1,
                mime_type="application/pdf",
                uploaded_by=1,
            )

    def test_taille_trop_grande_raise_error(self):
        """Verifie l'erreur pour taille depassant 10 Go."""
        with pytest.raises(ValueError, match="10 Go"):
            Document(
                chantier_id=1,
                dossier_id=1,
                nom="test.pdf",
                nom_original="test.pdf",
                chemin_stockage="/storage/test.pdf",
                taille=MAX_TAILLE_FICHIER + 1,
                mime_type="application/pdf",
                uploaded_by=1,
            )

    def test_extension_property(self):
        """Verifie la propriete extension."""
        doc_pdf = Document(
            chantier_id=1,
            dossier_id=1,
            nom="rapport.pdf",
            nom_original="rapport.pdf",
            chemin_stockage="/storage/rapport.pdf",
            taille=1024,
            mime_type="application/pdf",
            uploaded_by=1,
        )
        assert doc_pdf.extension == ".pdf"

        doc_sans_ext = Document(
            chantier_id=1,
            dossier_id=1,
            nom="fichier",
            nom_original="fichier",
            chemin_stockage="/storage/fichier",
            taille=1024,
            mime_type="application/octet-stream",
            uploaded_by=1,
        )
        assert doc_sans_ext.extension == ""

    def test_taille_formatee(self):
        """Verifie le formatage de la taille."""
        doc_octets = Document(
            chantier_id=1, dossier_id=1, nom="a.txt", nom_original="a.txt",
            chemin_stockage="/s/a.txt", taille=500, mime_type="text/plain", uploaded_by=1,
        )
        assert "o" in doc_octets.taille_formatee

        doc_ko = Document(
            chantier_id=1, dossier_id=1, nom="b.txt", nom_original="b.txt",
            chemin_stockage="/s/b.txt", taille=2048, mime_type="text/plain", uploaded_by=1,
        )
        assert "Ko" in doc_ko.taille_formatee

        doc_mo = Document(
            chantier_id=1, dossier_id=1, nom="c.pdf", nom_original="c.pdf",
            chemin_stockage="/s/c.pdf", taille=5 * 1024 * 1024, mime_type="application/pdf", uploaded_by=1,
        )
        assert "Mo" in doc_mo.taille_formatee

        doc_go = Document(
            chantier_id=1, dossier_id=1, nom="d.mp4", nom_original="d.mp4",
            chemin_stockage="/s/d.mp4", taille=2 * 1024 * 1024 * 1024, mime_type="video/mp4", uploaded_by=1,
        )
        assert "Go" in doc_go.taille_formatee

    def test_icone_property(self):
        """Verifie la propriete icone."""
        doc = Document(
            chantier_id=1, dossier_id=1, nom="a.pdf", nom_original="a.pdf",
            chemin_stockage="/s/a.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        assert doc.icone == "file-pdf"

    def test_detection_type_automatique(self):
        """Verifie la detection automatique du type depuis l'extension."""
        doc = Document(
            chantier_id=1, dossier_id=1, nom="image.png", nom_original="image.png",
            chemin_stockage="/s/image.png", taille=1024, mime_type="image/png", uploaded_by=1,
        )
        assert doc.type_document == TypeDocument.IMAGE

    def test_peut_acceder_uploadeur(self):
        """L'uploadeur a toujours acces."""
        doc = Document(
            chantier_id=1, dossier_id=1, nom="a.pdf", nom_original="a.pdf",
            chemin_stockage="/s/a.pdf", taille=1024, mime_type="application/pdf", uploaded_by=5,
            niveau_acces=NiveauAcces.ADMIN,
        )
        assert doc.peut_acceder("compagnon", user_id=5) is True

    def test_peut_acceder_autorisation_nominative(self):
        """Acces via autorisation nominative."""
        doc = Document(
            chantier_id=1, dossier_id=1, nom="a.pdf", nom_original="a.pdf",
            chemin_stockage="/s/a.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
            niveau_acces=NiveauAcces.ADMIN,
        )
        assert doc.peut_acceder("compagnon", user_id=10, autorisations_nominatives=[10, 20]) is True

    def test_peut_acceder_niveau_propre(self):
        """Acces via niveau propre du document."""
        doc = Document(
            chantier_id=1, dossier_id=1, nom="a.pdf", nom_original="a.pdf",
            chemin_stockage="/s/a.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
            niveau_acces=NiveauAcces.CHEF_CHANTIER,
        )
        assert doc.peut_acceder("chef_chantier") is True
        assert doc.peut_acceder("compagnon") is False

    def test_peut_acceder_niveau_dossier(self):
        """Acces herite du niveau dossier."""
        doc = Document(
            chantier_id=1, dossier_id=1, nom="a.pdf", nom_original="a.pdf",
            chemin_stockage="/s/a.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
            niveau_acces=None,
        )
        assert doc.peut_acceder("conducteur", niveau_dossier=NiveauAcces.CONDUCTEUR) is True
        assert doc.peut_acceder("chef_chantier", niveau_dossier=NiveauAcces.CONDUCTEUR) is False

    def test_renommer(self):
        """Test du renommage."""
        doc = Document(
            chantier_id=1, dossier_id=1, nom="ancien.pdf", nom_original="ancien.pdf",
            chemin_stockage="/s/ancien.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        old_updated = doc.updated_at
        doc.renommer("nouveau.pdf")
        assert doc.nom == "nouveau.pdf"
        assert doc.updated_at >= old_updated

    def test_renommer_vide_raise_error(self):
        """Verifie l'erreur pour renommage avec nom vide."""
        doc = Document(
            chantier_id=1, dossier_id=1, nom="test.pdf", nom_original="test.pdf",
            chemin_stockage="/s/test.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        with pytest.raises(ValueError, match="nom du document"):
            doc.renommer("")

    def test_deplacer(self):
        """Test du deplacement."""
        doc = Document(
            chantier_id=1, dossier_id=1, nom="a.pdf", nom_original="a.pdf",
            chemin_stockage="/s/a.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        doc.deplacer(5)
        assert doc.dossier_id == 5

    def test_changer_niveau_acces(self):
        """Test du changement de niveau d'acces."""
        doc = Document(
            chantier_id=1, dossier_id=1, nom="a.pdf", nom_original="a.pdf",
            chemin_stockage="/s/a.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        doc.changer_niveau_acces(NiveauAcces.ADMIN)
        assert doc.niveau_acces == NiveauAcces.ADMIN

        doc.changer_niveau_acces(None)
        assert doc.niveau_acces is None

    def test_incrementer_version(self):
        """Test de l'incrementation de version."""
        doc = Document(
            chantier_id=1, dossier_id=1, nom="a.pdf", nom_original="a.pdf",
            chemin_stockage="/s/a.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        assert doc.version == 1
        doc.incrementer_version()
        assert doc.version == 2

    def test_valider_taille(self):
        """Test de validation de taille."""
        assert Document.valider_taille(0) is True
        assert Document.valider_taille(1024) is True
        assert Document.valider_taille(MAX_TAILLE_FICHIER) is True
        assert Document.valider_taille(MAX_TAILLE_FICHIER + 1) is False
        assert Document.valider_taille(-1) is False

    def test_valider_extension(self):
        """Test de validation d'extension."""
        assert Document.valider_extension(".pdf") is True
        assert Document.valider_extension("pdf") is True
        assert Document.valider_extension(".png") is True
        assert Document.valider_extension(".xlsx") is True
        assert Document.valider_extension(".xyz") is False

    def test_equality(self):
        """Test de l'egalite."""
        doc1 = Document(
            id=1, chantier_id=1, dossier_id=1, nom="a.pdf", nom_original="a.pdf",
            chemin_stockage="/s/a.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        doc2 = Document(
            id=1, chantier_id=2, dossier_id=2, nom="b.pdf", nom_original="b.pdf",
            chemin_stockage="/s/b.pdf", taille=2048, mime_type="application/pdf", uploaded_by=2,
        )
        doc3 = Document(
            id=2, chantier_id=1, dossier_id=1, nom="a.pdf", nom_original="a.pdf",
            chemin_stockage="/s/a.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        assert doc1 == doc2  # Meme ID
        assert doc1 != doc3  # ID differents

    def test_hash(self):
        """Test du hash."""
        doc1 = Document(
            id=1, chantier_id=1, dossier_id=1, nom="a.pdf", nom_original="a.pdf",
            chemin_stockage="/s/a.pdf", taille=1024, mime_type="application/pdf", uploaded_by=1,
        )
        doc2 = Document(
            id=1, chantier_id=2, dossier_id=2, nom="b.pdf", nom_original="b.pdf",
            chemin_stockage="/s/b.pdf", taille=2048, mime_type="application/pdf", uploaded_by=2,
        )
        assert hash(doc1) == hash(doc2)


class TestDossier:
    """Tests pour Dossier."""

    def test_create_dossier_minimal(self):
        """Creation d'un dossier avec donnees minimales."""
        dossier = Dossier(chantier_id=1, nom="Plans")
        assert dossier.chantier_id == 1
        assert dossier.nom == "Plans"
        assert dossier.type_dossier == DossierType.CUSTOM
        assert dossier.niveau_acces == NiveauAcces.COMPAGNON
        assert dossier.parent_id is None
        assert dossier.ordre == 0

    def test_create_dossier_complet(self):
        """Creation d'un dossier avec toutes les donnees."""
        dossier = Dossier(
            chantier_id=1,
            nom="Documents administratifs",
            type_dossier=DossierType.ADMINISTRATIF,
            niveau_acces=NiveauAcces.CONDUCTEUR,
            parent_id=5,
            ordre=2,
        )
        assert dossier.type_dossier == DossierType.ADMINISTRATIF
        assert dossier.niveau_acces == NiveauAcces.CONDUCTEUR
        assert dossier.parent_id == 5
        assert dossier.ordre == 2

    def test_nom_vide_raise_error(self):
        """Verifie l'erreur pour nom vide."""
        with pytest.raises(ValueError, match="nom du dossier"):
            Dossier(chantier_id=1, nom="")

    def test_nom_espaces_raise_error(self):
        """Verifie l'erreur pour nom avec espaces uniquement."""
        with pytest.raises(ValueError, match="nom du dossier"):
            Dossier(chantier_id=1, nom="   ")

    def test_chemin_complet_custom(self):
        """Verifie le chemin complet pour dossier custom."""
        dossier = Dossier(chantier_id=1, nom="Mon Dossier", type_dossier=DossierType.CUSTOM)
        assert dossier.chemin_complet == "Mon Dossier"

    def test_chemin_complet_type_standard(self):
        """Verifie le chemin complet pour dossier type."""
        dossier = Dossier(chantier_id=1, nom="Plans", type_dossier=DossierType.PLANS)
        assert dossier.chemin_complet == "01 - Plans"

    def test_peut_acceder_compagnon(self):
        """Test d'acces niveau compagnon."""
        dossier = Dossier(chantier_id=1, nom="Plans", niveau_acces=NiveauAcces.COMPAGNON)
        assert dossier.peut_acceder("compagnon") is True
        assert dossier.peut_acceder("admin") is True

    def test_peut_acceder_niveau_restrictif(self):
        """Test d'acces niveau restrictif."""
        dossier = Dossier(chantier_id=1, nom="Admin", niveau_acces=NiveauAcces.ADMIN)
        assert dossier.peut_acceder("compagnon") is False
        assert dossier.peut_acceder("chef_chantier") is False
        assert dossier.peut_acceder("conducteur") is False
        assert dossier.peut_acceder("admin") is True

    def test_peut_acceder_autorisation_nominative(self):
        """Test d'acces via autorisation nominative."""
        dossier = Dossier(chantier_id=1, nom="Admin", niveau_acces=NiveauAcces.ADMIN)
        assert dossier.peut_acceder("compagnon", user_id=10, autorisations_nominatives=[10, 20]) is True

    def test_changer_niveau_acces(self):
        """Test du changement de niveau d'acces."""
        dossier = Dossier(chantier_id=1, nom="Test", niveau_acces=NiveauAcces.COMPAGNON)
        old_updated = dossier.updated_at
        dossier.changer_niveau_acces(NiveauAcces.CONDUCTEUR)
        assert dossier.niveau_acces == NiveauAcces.CONDUCTEUR
        assert dossier.updated_at >= old_updated

    def test_renommer(self):
        """Test du renommage."""
        dossier = Dossier(chantier_id=1, nom="Ancien Nom")
        dossier.renommer("Nouveau Nom")
        assert dossier.nom == "Nouveau Nom"

    def test_renommer_vide_raise_error(self):
        """Verifie l'erreur pour renommage avec nom vide."""
        dossier = Dossier(chantier_id=1, nom="Test")
        with pytest.raises(ValueError, match="nom du dossier"):
            dossier.renommer("")

    def test_deplacer(self):
        """Test du deplacement."""
        dossier = Dossier(chantier_id=1, nom="Test", parent_id=None)
        dossier.deplacer(5)
        assert dossier.parent_id == 5

        dossier.deplacer(None)
        assert dossier.parent_id is None

    def test_equality(self):
        """Test de l'egalite."""
        d1 = Dossier(id=1, chantier_id=1, nom="A")
        d2 = Dossier(id=1, chantier_id=2, nom="B")
        d3 = Dossier(id=2, chantier_id=1, nom="A")
        assert d1 == d2
        assert d1 != d3

    def test_hash(self):
        """Test du hash."""
        d1 = Dossier(id=1, chantier_id=1, nom="A")
        d2 = Dossier(id=1, chantier_id=2, nom="B")
        assert hash(d1) == hash(d2)


class TestAutorisationDocument:
    """Tests pour AutorisationDocument."""

    def test_create_autorisation_dossier(self):
        """Creation d'une autorisation sur dossier."""
        autorisation = AutorisationDocument(
            user_id=1,
            type_autorisation=TypeAutorisation.LECTURE,
            accorde_par=2,
            dossier_id=5,
        )
        assert autorisation.user_id == 1
        assert autorisation.type_autorisation == TypeAutorisation.LECTURE
        assert autorisation.dossier_id == 5
        assert autorisation.document_id is None
        assert autorisation.cible == "dossier"
        assert autorisation.cible_id == 5

    def test_create_autorisation_document(self):
        """Creation d'une autorisation sur document."""
        autorisation = AutorisationDocument(
            user_id=1,
            type_autorisation=TypeAutorisation.ECRITURE,
            accorde_par=2,
            document_id=10,
        )
        assert autorisation.document_id == 10
        assert autorisation.dossier_id is None
        assert autorisation.cible == "document"
        assert autorisation.cible_id == 10

    def test_create_sans_cible_raise_error(self):
        """Verifie l'erreur si pas de dossier ni document."""
        with pytest.raises(ValueError, match="dossier ou un document"):
            AutorisationDocument(
                user_id=1,
                type_autorisation=TypeAutorisation.LECTURE,
                accorde_par=2,
            )

    def test_create_deux_cibles_raise_error(self):
        """Verifie l'erreur si dossier ET document."""
        with pytest.raises(ValueError, match="un seul"):
            AutorisationDocument(
                user_id=1,
                type_autorisation=TypeAutorisation.LECTURE,
                accorde_par=2,
                dossier_id=5,
                document_id=10,
            )

    def test_est_valide_sans_expiration(self):
        """Autorisation valide sans date d'expiration."""
        autorisation = AutorisationDocument(
            user_id=1,
            type_autorisation=TypeAutorisation.LECTURE,
            accorde_par=2,
            dossier_id=5,
        )
        assert autorisation.est_valide is True

    def test_est_valide_expiration_future(self):
        """Autorisation valide avec expiration future."""
        autorisation = AutorisationDocument(
            user_id=1,
            type_autorisation=TypeAutorisation.LECTURE,
            accorde_par=2,
            dossier_id=5,
            expire_at=datetime.now() + timedelta(days=30),
        )
        assert autorisation.est_valide is True

    def test_est_valide_expiree(self):
        """Autorisation expiree."""
        autorisation = AutorisationDocument(
            user_id=1,
            type_autorisation=TypeAutorisation.LECTURE,
            accorde_par=2,
            dossier_id=5,
            expire_at=datetime.now() - timedelta(days=1),
        )
        assert autorisation.est_valide is False

    def test_peut_lire_lecture(self):
        """Autorisation LECTURE permet la lecture."""
        autorisation = AutorisationDocument(
            user_id=1,
            type_autorisation=TypeAutorisation.LECTURE,
            accorde_par=2,
            dossier_id=5,
        )
        assert autorisation.peut_lire() is True
        assert autorisation.peut_ecrire() is False
        assert autorisation.peut_supprimer() is False

    def test_peut_lire_ecriture(self):
        """Autorisation ECRITURE permet lecture et ecriture."""
        autorisation = AutorisationDocument(
            user_id=1,
            type_autorisation=TypeAutorisation.ECRITURE,
            accorde_par=2,
            dossier_id=5,
        )
        assert autorisation.peut_lire() is True
        assert autorisation.peut_ecrire() is True
        assert autorisation.peut_supprimer() is False

    def test_peut_lire_admin(self):
        """Autorisation ADMIN permet tout."""
        autorisation = AutorisationDocument(
            user_id=1,
            type_autorisation=TypeAutorisation.ADMIN,
            accorde_par=2,
            dossier_id=5,
        )
        assert autorisation.peut_lire() is True
        assert autorisation.peut_ecrire() is True
        assert autorisation.peut_supprimer() is True

    def test_autorisation_expiree_ne_peut_pas(self):
        """Autorisation expiree ne permet rien."""
        autorisation = AutorisationDocument(
            user_id=1,
            type_autorisation=TypeAutorisation.ADMIN,
            accorde_par=2,
            dossier_id=5,
            expire_at=datetime.now() - timedelta(days=1),
        )
        assert autorisation.peut_lire() is False
        assert autorisation.peut_ecrire() is False
        assert autorisation.peut_supprimer() is False

    def test_revoquer(self):
        """Test de revocation."""
        autorisation = AutorisationDocument(
            user_id=1,
            type_autorisation=TypeAutorisation.LECTURE,
            accorde_par=2,
            dossier_id=5,
        )
        assert autorisation.est_valide is True
        autorisation.revoquer()
        assert autorisation.est_valide is False

    def test_creer_pour_dossier(self):
        """Test du factory method pour dossier."""
        autorisation = AutorisationDocument.creer_pour_dossier(
            dossier_id=5,
            user_id=1,
            type_autorisation=TypeAutorisation.LECTURE,
            accorde_par=2,
        )
        assert autorisation.dossier_id == 5
        assert autorisation.document_id is None

    def test_creer_pour_document(self):
        """Test du factory method pour document."""
        autorisation = AutorisationDocument.creer_pour_document(
            document_id=10,
            user_id=1,
            type_autorisation=TypeAutorisation.ECRITURE,
            accorde_par=2,
        )
        assert autorisation.document_id == 10
        assert autorisation.dossier_id is None

    def test_creer_avec_expiration(self):
        """Test de creation avec date d'expiration."""
        expire = datetime.now() + timedelta(days=7)
        autorisation = AutorisationDocument.creer_pour_dossier(
            dossier_id=5,
            user_id=1,
            type_autorisation=TypeAutorisation.LECTURE,
            accorde_par=2,
            expire_at=expire,
        )
        assert autorisation.expire_at == expire

    def test_equality(self):
        """Test de l'egalite."""
        a1 = AutorisationDocument(
            id=1, user_id=1, type_autorisation=TypeAutorisation.LECTURE,
            accorde_par=2, dossier_id=5,
        )
        a2 = AutorisationDocument(
            id=1, user_id=2, type_autorisation=TypeAutorisation.ECRITURE,
            accorde_par=3, document_id=10,
        )
        a3 = AutorisationDocument(
            id=2, user_id=1, type_autorisation=TypeAutorisation.LECTURE,
            accorde_par=2, dossier_id=5,
        )
        assert a1 == a2
        assert a1 != a3

    def test_hash(self):
        """Test du hash."""
        a1 = AutorisationDocument(
            id=1, user_id=1, type_autorisation=TypeAutorisation.LECTURE,
            accorde_par=2, dossier_id=5,
        )
        a2 = AutorisationDocument(
            id=1, user_id=2, type_autorisation=TypeAutorisation.ECRITURE,
            accorde_par=3, document_id=10,
        )
        assert hash(a1) == hash(a2)
