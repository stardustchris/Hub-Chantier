#!/usr/bin/env python3
"""
Script pour ajouter une évolution financière mensuelle au chantier TRIALP.
Crée des achats et situations étalées sur 6 mois pour voir l'évolution.
"""

import os
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal

# Ajouter le chemin du backend pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from shared.infrastructure.database import SessionLocal, init_db
from modules.financier.infrastructure.persistence.models import (
    BudgetModel,
    LotBudgetaireModel,
    AchatModel,
    FournisseurModel,
    SituationTravauxModel,
)
from modules.chantiers.infrastructure.persistence.chantier_model import ChantierModel


def create_monthly_timeline(db: Session):
    """Crée une évolution financière sur 6 mois pour TRIALP."""

    print("\n=== Création de l'évolution financière TRIALP (6 mois) ===\n")

    # Récupérer le chantier TRIALP
    chantier = db.query(ChantierModel).filter(
        ChantierModel.code == "2025-11-TRIALP"
    ).first()

    if not chantier:
        print("❌ Chantier TRIALP non trouvé")
        return

    budget = db.query(BudgetModel).filter(
        BudgetModel.chantier_id == chantier.id
    ).first()

    if not budget:
        print("❌ Budget TRIALP non trouvé")
        return

    # Récupérer les lots
    lots = db.query(LotBudgetaireModel).filter(
        LotBudgetaireModel.budget_id == budget.id
    ).all()

    lots_by_code = {lot.code_lot: lot for lot in lots}

    # Récupérer le fournisseur
    fournisseur = db.query(FournisseurModel).first()

    if not fournisseur:
        print("❌ Aucun fournisseur trouvé")
        return

    # Définir la timeline sur 6 mois (novembre 2025 à avril 2026)
    today = date.today()

    timeline = [
        # Mois 1 : Novembre 2025 - Démarrage (terrassement)
        {
            "mois": "2025-11",
            "date_debut": date(2025, 11, 1),
            "date_fin": date(2025, 11, 30),
            "achats": [
                ("TERRASSEMENT", "Terrassement phase 1", 300, "m3", 280.00, "livre", -60),
                ("TERRASSEMENT", "Évacuation terres", 200, "m3", 25.00, "livre", -58),
            ],
            "situation": {
                "numero": "SIT-2025-11",
                "montant_periode": 89000.00,  # ~7% du budget
                "statut": "validee",
            }
        },
        # Mois 2 : Décembre 2025 - Fondations
        {
            "mois": "2025-12",
            "date_debut": date(2025, 12, 1),
            "date_fin": date(2025, 12, 31),
            "achats": [
                ("TERRASSEMENT", "Terrassement phase 2", 250, "m3", 280.00, "livre", -35),
                ("FONDATIONS", "Béton C30/37 semelles", 180, "m3", 450.00, "livre", -32),
                ("FONDATIONS", "Ferraillage fondations", 8000, "kg", 1.20, "livre", -30),
            ],
            "situation": {
                "numero": "SIT-2025-12",
                "montant_periode": 180000.00,  # ~15% du budget
                "statut": "validee",
            }
        },
        # Mois 3 : Janvier 2026 - Dalles et voiles
        {
            "mois": "2026-01",
            "date_debut": date(2026, 1, 1),
            "date_fin": date(2026, 1, 31),
            "achats": [
                ("FONDATIONS", "Béton fondations finale", 120, "m3", 450.00, "livre", -5),
                ("DALLE-BA", "Béton C25/30 dalle RDC", 400, "m3", 180.00, "livre", -3),
                ("DALLE-BA", "Ferraillage dalles", 12000, "kg", 1.10, "commande", -1),
                ("VOILES-BA", "Béton C30/37 voiles", 200, "m3", 320.00, "valide", 5),
            ],
            "situation": {
                "numero": "SIT-2026-01",
                "montant_periode": 240000.00,  # ~20% du budget
                "statut": "validee",
            }
        },
        # Mois 4 : Février 2026 (mois actuel) - Suite voiles
        {
            "mois": "2026-02",
            "date_debut": date(2026, 2, 1),
            "date_fin": date(2026, 2, 28),
            "achats": [
                ("DALLE-BA", "Béton dalle étages", 450, "m3", 180.00, "livre", -18),
                ("VOILES-BA", "Béton voiles étages", 280, "m3", 320.00, "commande", -10),
                ("VOILES-BA", "Ferraillage voiles", 15000, "kg", 1.15, "valide", -5),
                ("POTEAUX-POUTRES", "Béton poteaux", 150, "m3", 520.00, "demande", 2),
            ],
            "situation": {
                "numero": "SIT-2026-02",
                "montant_periode": 195000.00,  # ~16% du budget
                "statut": "brouillon",  # En cours
            }
        },
        # Mois 5 : Mars 2026 (prévisionnel) - Poteaux et planchers
        {
            "mois": "2026-03",
            "date_debut": date(2026, 3, 1),
            "date_fin": date(2026, 3, 31),
            "achats": [
                ("POTEAUX-POUTRES", "Béton poutres", 130, "m3", 520.00, "demande", 25),
                ("PLANCHERS", "Planchers préfab étage 1", 400, "m2", 195.00, "demande", 28),
            ],
            "situation": None  # Prévisionnel
        },
        # Mois 6 : Avril 2026 (prévisionnel) - Suite planchers
        {
            "mois": "2026-04",
            "date_debut": date(2026, 4, 1),
            "date_fin": date(2026, 4, 30),
            "achats": [
                ("PLANCHERS", "Planchers préfab étage 2", 550, "m2", 195.00, "demande", 55),
            ],
            "situation": None  # Prévisionnel
        },
    ]

    admin_id = 1
    total_achats = 0
    total_situations = 0

    # Supprimer les achats existants pour TRIALP
    existing_achats = db.query(AchatModel).filter(
        AchatModel.chantier_id == chantier.id
    ).all()
    for achat in existing_achats:
        db.delete(achat)
    print(f"🗑️  Supprimé {len(existing_achats)} achats existants\n")

    # Supprimer les situations existantes pour TRIALP
    existing_sits = db.query(SituationTravauxModel).filter(
        SituationTravauxModel.chantier_id == chantier.id
    ).all()
    for sit in existing_sits:
        db.delete(sit)
    print(f"🗑️  Supprimé {len(existing_sits)} situations existantes\n")

    db.commit()

    montant_cumule = 0

    for periode in timeline:
        print(f"📅 {periode['mois']}")

        # Créer les achats
        for achat_data in periode['achats']:
            code_lot, libelle, qte, unite, px_unit, statut, jours_offset = achat_data

            lot = lots_by_code.get(code_lot)
            if not lot:
                continue

            date_commande = periode['date_debut'] + timedelta(days=abs(jours_offset))

            achat = AchatModel(
                chantier_id=chantier.id,
                fournisseur_id=fournisseur.id,
                lot_budgetaire_id=lot.id,
                type_achat="materiau",
                libelle=libelle,
                quantite=qte,
                unite=unite,
                prix_unitaire_ht=px_unit,
                taux_tva=20.0,
                date_commande=date_commande,
                statut=statut,
                demandeur_id=admin_id,
                valideur_id=admin_id if statut in ["valide", "commande", "livre"] else None,
                validated_at=date_commande + timedelta(days=1) if statut in ["valide", "commande", "livre"] else None,
                created_by=admin_id,
            )
            db.add(achat)
            total_achats += 1
            print(f"   ✅ Achat: {libelle} ({qte} {unite} × {px_unit}€) - {statut}")

        # Créer la situation si définie
        if periode['situation']:
            sit_data = periode['situation']
            montant_periode = sit_data['montant_periode']
            montant_cumule += montant_periode

            situation = SituationTravauxModel(
                chantier_id=chantier.id,
                budget_id=budget.id,
                numero=sit_data['numero'],
                periode_debut=periode['date_debut'],
                periode_fin=periode['date_fin'],
                montant_cumule_precedent_ht=montant_cumule - montant_periode,
                montant_periode_ht=montant_periode,
                montant_cumule_ht=montant_cumule,
                retenue_garantie_pct=5.0,
                taux_tva=20.0,
                statut=sit_data['statut'],
                created_by=admin_id,
                emise_at=periode['date_fin'] if sit_data['statut'] != 'brouillon' else None,
                validated_at=periode['date_fin'] + timedelta(days=2) if sit_data['statut'] == 'validee' else None,
                validated_by=admin_id if sit_data['statut'] == 'validee' else None,
            )
            db.add(situation)
            total_situations += 1
            print(f"   📋 Situation: {sit_data['numero']} - {montant_periode:,.0f}€ HT (cumul: {montant_cumule:,.0f}€) - {sit_data['statut']}")

        print()

    db.commit()

    print(f"\n✅ Évolution créée:")
    print(f"   • {total_achats} achats sur 6 mois")
    print(f"   • {total_situations} situations de travaux")
    print(f"   • Montant cumulé: {montant_cumule:,.0f}€ HT ({montant_cumule/1200000*100:.1f}% du budget)")


if __name__ == "__main__":
    init_db()
    db = SessionLocal()

    try:
        create_monthly_timeline(db)
        print("\n🎉 Timeline financière créée avec succès!")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
