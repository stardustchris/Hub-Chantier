"""
Script de seed pour peupler les documents avec des données de démonstration.

Usage:
    python scripts/seed_documents_demo.py

Ce script crée :
- Des dossiers dans l'arborescence standard
- Des documents de démonstration dans chaque dossier
- Des données réalistes pour tester la GED
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from shared.infrastructure.database import get_db
from modules.documents.infrastructure.persistence.document_model import DocumentModel
from modules.documents.infrastructure.persistence.dossier_model import DossierModel
from modules.chantiers.infrastructure.persistence.chantier_model import ChantierModel


def create_demo_documents(db: Session):
    """Crée des documents de démonstration dans les dossiers existants."""
    
    print("🔍 Recherche des chantiers avec arborescence...")
    
    # Récupérer le premier chantier qui a des dossiers
    chantier = db.query(ChantierModel).first()
    if not chantier:
        print("❌ Aucun chantier trouvé. Créez d'abord un chantier.")
        return
    
    print(f"✅ Chantier trouvé : {chantier.code} - {chantier.nom}")
    
    # Récupérer les dossiers du chantier
    dossiers = db.query(DossierModel).filter(
        DossierModel.chantier_id == chantier.id
    ).all()
    
    if not dossiers:
        print(f"⚠️  Aucun dossier trouvé pour ce chantier. Initialisez l'arborescence d'abord.")
        return
    
    print(f"✅ {len(dossiers)} dossiers trouvés")
    
    # Documents de démonstration par type de dossier
    demo_documents = {
        "01_plans": [
            {
                "nom": "Plan masse chantier.pdf",
                "description": "Plan d'implantation général du chantier",
                "type_document": "pdf",
                "taille": 2_456_789,
                "chemin_fichier": "/demo/plans/plan_masse.pdf",
            },
            {
                "nom": "Plan facade principale.dwg",
                "description": "Plans d'exécution - Façade sud",
                "type_document": "autre",
                "taille": 1_234_567,
                "chemin_fichier": "/demo/plans/facade_principale.dwg",
            },
            {
                "nom": "Détails techniques fondations.pdf",
                "description": "Notes de calcul et détails de ferraillage",
                "type_document": "pdf",
                "taille": 3_456_789,
                "chemin_fichier": "/demo/plans/details_fondations.pdf",
            },
        ],
        "02_administratif": [
            {
                "nom": "Permis de construire PC-2026-001.pdf",
                "description": "Permis de construire validé par la mairie",
                "type_document": "pdf",
                "taille": 1_876_543,
                "chemin_fichier": "/demo/admin/permis_construire.pdf",
            },
            {
                "nom": "Contrat entreprise générale.pdf",
                "description": "Contrat signé avec Greg Construction",
                "type_document": "pdf",
                "taille": 987_654,
                "chemin_fichier": "/demo/admin/contrat.pdf",
            },
            {
                "nom": "Devis électricité signé.pdf",
                "description": "Devis sous-traitant électricité accepté",
                "type_document": "pdf",
                "taille": 456_789,
                "chemin_fichier": "/demo/admin/devis_elec.pdf",
            },
        ],
        "03_securite": [
            {
                "nom": "PPSPS Version 2.pdf",
                "description": "Plan Particulier de Sécurité et Protection de la Santé",
                "type_document": "pdf",
                "taille": 4_567_890,
                "chemin_fichier": "/demo/secu/ppsps_v2.pdf",
            },
            {
                "nom": "Registre sécurité chantier.xlsx",
                "description": "Suivi quotidien des mesures de sécurité",
                "type_document": "excel",
                "taille": 234_567,
                "chemin_fichier": "/demo/secu/registre.xlsx",
            },
            {
                "nom": "Photos EPI équipes.jpg",
                "description": "Vérification port des équipements de protection",
                "type_document": "image",
                "taille": 3_456_789,
                "chemin_fichier": "/demo/secu/photos_epi.jpg",
            },
        ],
        "04_qualite": [
            {
                "nom": "PV réception béton lot 1.pdf",
                "description": "Procès-verbal réception béton fondations",
                "type_document": "pdf",
                "taille": 876_543,
                "chemin_fichier": "/demo/qualite/pv_beton_lot1.pdf",
            },
            {
                "nom": "Fiche autocontrôle étanchéité.pdf",
                "description": "Contrôles étanchéité toiture",
                "type_document": "pdf",
                "taille": 567_890,
                "chemin_fichier": "/demo/qualite/autocontrole_etancheite.pdf",
            },
        ],
        "05_photos": [
            {
                "nom": "Avancement semaine 12.jpg",
                "description": "Photo progression générale du chantier",
                "type_document": "image",
                "taille": 5_678_901,
                "chemin_fichier": "/demo/photos/avancement_s12.jpg",
            },
            {
                "nom": "Pose première pierre.mp4",
                "description": "Vidéo cérémonie pose première pierre",
                "type_document": "video",
                "taille": 45_678_901,
                "chemin_fichier": "/demo/photos/premiere_pierre.mp4",
            },
            {
                "nom": "Charpente terminée.jpg",
                "description": "Finalisation du lot charpente",
                "type_document": "image",
                "taille": 4_567_890,
                "chemin_fichier": "/demo/photos/charpente.jpg",
            },
        ],
        "06_comptes_rendus": [
            {
                "nom": "CR réunion chantier 2026-01-15.docx",
                "description": "Compte-rendu hebdomadaire avec tous corps d'état",
                "type_document": "word",
                "taille": 234_567,
                "chemin_fichier": "/demo/cr/reunion_20260115.docx",
            },
            {
                "nom": "CR visite OPC 2026-01-20.pdf",
                "description": "Rapport de visite Ordonnancement Pilotage Coordination",
                "type_document": "pdf",
                "taille": 678_901,
                "chemin_fichier": "/demo/cr/visite_opc.pdf",
            },
        ],
        "07_livraisons": [
            {
                "nom": "BL béton 250m³ - 12 janvier.pdf",
                "description": "Bon de livraison béton prêt à l'emploi",
                "type_document": "pdf",
                "taille": 345_678,
                "chemin_fichier": "/demo/livraisons/bl_beton_20260112.pdf",
            },
            {
                "nom": "BL parpaings - 18 janvier.pdf",
                "description": "Livraison 2000 parpaings 20x20x50",
                "type_document": "pdf",
                "taille": 234_567,
                "chemin_fichier": "/demo/livraisons/bl_parpaings.pdf",
            },
        ],
    }
    
    print("\n📄 Création des documents de démonstration...")
    
    total_created = 0
    for dossier in dossiers:
        type_dossier = dossier.type_dossier
        
        if type_dossier not in demo_documents:
            continue
        
        documents_config = demo_documents[type_dossier]
        
        print(f"\n  📁 Dossier: {dossier.nom}")
        
        for i, doc_config in enumerate(documents_config):
            # Créer le document
            document = DocumentModel(
                dossier_id=dossier.id,
                nom=doc_config["nom"],
                description=doc_config["description"],
                type_document=doc_config["type_document"],
                taille=doc_config["taille"],
                chemin_fichier=doc_config["chemin_fichier"],
                version=1,
                uploaded_by=1,  # Admin
                created_at=datetime.now() - timedelta(days=10-i),
                updated_at=datetime.now() - timedelta(days=10-i),
            )
            
            db.add(document)
            total_created += 1
            print(f"    ✅ {doc_config['nom']} ({doc_config['type_document']})")
    
    db.commit()
    
    print(f"\n✨ {total_created} documents de démonstration créés avec succès !")
    print(f"\n💡 Rafraîchissez la page Documents pour voir les données.")


if __name__ == "__main__":
    print("=" * 60)
    print("🌱 SEED DOCUMENTS DE DÉMONSTRATION")
    print("=" * 60)
    
    db = next(get_db())
    try:
        create_demo_documents(db)
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    print("\n" + "=" * 60)
