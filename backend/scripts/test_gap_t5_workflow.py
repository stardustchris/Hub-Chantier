#!/usr/bin/env python3
"""
Script de test manuel : GAP-T5 - Workflow Affectation → Pointage (FDH-10).

Ce script permet de tester manuellement le workflow de création automatique
de pointages depuis les affectations, en environnement seed.

Usage:
    cd backend
    python3 -m scripts.test_gap_t5_workflow

Le script:
1. Charge la base seed
2. Crée une affectation avec heures_prevues=4.0
3. Vérifie que le pointage créé a bien 04:00 (ou 08:00 si bug)
4. Affiche un rapport détaillé
"""

import sys
import os
from datetime import date

# Ajouter le chemin du backend pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from shared.infrastructure.database import SessionLocal, init_db
from shared.infrastructure.event_bus import event_bus

# Initialiser la DB
init_db()

# Câbler l'intégration Planning → Pointages (FDH-10)
from modules.pointages.infrastructure.event_handlers import setup_planning_integration
setup_planning_integration(SessionLocal)
print("✅ Intégration Planning → Pointages câblée")

# Récupérer une session
db: Session = SessionLocal()

try:
    # ==========================================================================
    # ETAPE 1: Récupérer des données de test
    # ==========================================================================
    print("\n" + "="*70)
    print("ETAPE 1 : Récupération des données de test")
    print("="*70)

    from modules.auth.infrastructure.persistence.user_model import UserModel
    from modules.chantiers.infrastructure.persistence.chantier_model import ChantierModel

    # Récupérer un utilisateur actif (ouvrier)
    user = db.query(UserModel).filter(
        UserModel.role.in_(["ouvrier", "chef_equipe"]),
        UserModel.is_active == True
    ).first()

    if not user:
        print("❌ Aucun utilisateur actif trouvé dans la base seed")
        sys.exit(1)

    print(f"✅ Utilisateur: {user.prenom} {user.nom} (ID={user.id})")

    # Récupérer un chantier actif (pas CONGES/MALADIE/etc)
    chantier = db.query(ChantierModel).filter(
        ChantierModel.statut == "en_cours",
        ~ChantierModel.code.in_(["CONGES", "MALADIE", "RTT", "FORMATION"])
    ).first()

    if not chantier:
        print("❌ Aucun chantier actif trouvé dans la base seed")
        sys.exit(1)

    print(f"✅ Chantier: {chantier.nom} (ID={chantier.id}, code={chantier.code})")

    # ==========================================================================
    # ETAPE 2: Créer une affectation avec heures_prevues=4.0
    # ==========================================================================
    print("\n" + "="*70)
    print("ETAPE 2 : Création d'une affectation avec heures_prevues=4.0")
    print("="*70)

    from modules.planning.infrastructure.persistence import SQLAlchemyAffectationRepository
    from modules.planning.application.use_cases import CreateAffectationUseCase
    from modules.planning.application.dtos import CreateAffectationDTO
    from modules.planning.infrastructure.event_bus_impl import PlanningEventBus
    from modules.chantiers.infrastructure.persistence import SQLAlchemyChantierRepository
    from modules.auth.infrastructure.persistence import SQLAlchemyUserRepository

    affectation_repo = SQLAlchemyAffectationRepository(db)
    chantier_repo = SQLAlchemyChantierRepository(db)
    user_repo = SQLAlchemyUserRepository(db)
    planning_event_bus = PlanningEventBus()

    # Enregistrer le handler sur l'event bus
    from modules.pointages.infrastructure.event_handlers import handle_affectation_created

    def wrapped_handler(event):
        """Handler avec session."""
        handle_affectation_created(event, db)

    planning_event_bus.subscribe('affectation.created', wrapped_handler)

    # Use case
    use_case = CreateAffectationUseCase(
        affectation_repo=affectation_repo,
        event_bus=planning_event_bus,
        chantier_repo=chantier_repo,
        user_repo=user_repo,
    )

    # DTO avec heures_prevues=4.0 (demi-journée)
    dto = CreateAffectationDTO(
        utilisateur_id=user.id,
        chantier_id=chantier.id,
        date=date(2026, 2, 15),  # Date future
        heures_prevues=4.0,  # ✅ Demi-journée
        type_affectation="unique",
    )

    print(f"📝 Création affectation:")
    print(f"   - Utilisateur: {user.prenom} {user.nom} (ID={user.id})")
    print(f"   - Chantier: {chantier.nom} (ID={chantier.id})")
    print(f"   - Date: 2026-02-15")
    print(f"   - Heures prévues: 4.0h (demi-journée)")

    # Créer l'affectation
    affectations = use_case.execute(dto, created_by=1)
    db.commit()

    if len(affectations) != 1:
        print(f"❌ Erreur: {len(affectations)} affectations créées (attendu: 1)")
        sys.exit(1)

    affectation = affectations[0]
    print(f"✅ Affectation créée (ID={affectation.id})")
    print(f"   - heures_prevues (entity): {affectation.heures_prevues}h")

    # ==========================================================================
    # ETAPE 3: Vérifier que le pointage a été créé automatiquement
    # ==========================================================================
    print("\n" + "="*70)
    print("ETAPE 3 : Vérification du pointage créé automatiquement")
    print("="*70)

    from modules.pointages.infrastructure.persistence import SQLAlchemyPointageRepository

    pointage_repo = SQLAlchemyPointageRepository(db)

    pointages = pointage_repo.find_by_utilisateur_and_date(user.id, date(2026, 2, 15))

    if len(pointages) == 0:
        print("❌ ERREUR: Aucun pointage créé automatiquement")
        print("   → Le handler n'a pas été appelé ou a échoué")
        sys.exit(1)

    if len(pointages) > 1:
        print(f"⚠️  ATTENTION: {len(pointages)} pointages trouvés (attendu: 1)")

    pointage = pointages[0]
    print(f"✅ Pointage créé (ID={pointage.id})")
    print(f"   - affectation_id: {pointage.affectation_id}")
    print(f"   - utilisateur_id: {pointage.utilisateur_id}")
    print(f"   - chantier_id: {pointage.chantier_id}")
    print(f"   - date_pointage: {pointage.date_pointage}")
    print(f"   - heures_normales: {pointage.heures_normales}")

    # ==========================================================================
    # ETAPE 4: Rapport final
    # ==========================================================================
    print("\n" + "="*70)
    print("RAPPORT FINAL : GAP-T5 - FDH-10")
    print("="*70)

    # Vérifier les heures
    heures_attendues = "04:00"
    heures_reelles = str(pointage.heures_normales)

    if heures_reelles == heures_attendues:
        print(f"✅ SUCCESS: Le pointage a les bonnes heures")
        print(f"   - Affectation heures_prevues: {affectation.heures_prevues}h")
        print(f"   - Pointage heures_normales: {heures_reelles}")
        print(f"\n🎉 FDH-10 fonctionne correctement !")
    else:
        print(f"❌ FAILURE: Le pointage n'a PAS les bonnes heures")
        print(f"   - Affectation heures_prevues: {affectation.heures_prevues}h")
        print(f"   - Pointage heures_normales attendues: {heures_attendues}")
        print(f"   - Pointage heures_normales réelles: {heures_reelles}")
        print(f"\n⚠️  DIAGNOSTIC:")
        print(f"   Le pointage a {heures_reelles} au lieu de {heures_attendues}.")
        print(f"   Cela signifie que 'heures_prevues' n'est PAS transmis dans l'événement.")
        print(f"   Le handler utilise le fallback '08:00' par défaut.")
        print(f"\n📋 ACTIONS REQUISES:")
        print(f"   1. Modifier AffectationCreatedEvent pour inclure heures_prevues")
        print(f"   2. Modifier CreateAffectationUseCase pour passer heures_prevues à l'événement")
        print(f"   3. Relancer ce test pour vérifier la correction")
        sys.exit(1)

    # ==========================================================================
    # ETAPE 5: Test avec chantier système (CONGES)
    # ==========================================================================
    print("\n" + "="*70)
    print("ETAPE 5 : Test avec chantier système (CONGES)")
    print("="*70)

    chantier_conges = db.query(ChantierModel).filter(
        ChantierModel.code == "CONGES"
    ).first()

    if chantier_conges:
        print(f"✅ Chantier CONGES trouvé (ID={chantier_conges.id})")

        # Créer une affectation CONGES
        dto_conges = CreateAffectationDTO(
            utilisateur_id=user.id,
            chantier_id=chantier_conges.id,
            date=date(2026, 2, 16),
            type_affectation="unique",
        )

        affectations_conges = use_case.execute(dto_conges, created_by=1)
        db.commit()

        print(f"✅ Affectation CONGES créée (ID={affectations_conges[0].id})")

        # Vérifier qu'AUCUN pointage n'a été créé
        pointages_conges = pointage_repo.find_by_utilisateur_and_date(
            user.id, date(2026, 2, 16)
        )

        if len(pointages_conges) == 0:
            print(f"✅ Aucun pointage créé (comportement attendu)")
            print(f"   → Les chantiers système (CONGES) sont bien filtrés")
        else:
            print(f"❌ ERREUR: {len(pointages_conges)} pointage(s) créé(s)")
            print(f"   → Le filtre des chantiers système ne fonctionne PAS")
            sys.exit(1)
    else:
        print(f"⚠️  Chantier CONGES non trouvé, test skippé")

    print("\n" + "="*70)
    print("✅ TOUS LES TESTS SONT PASSÉS")
    print("="*70)

except Exception as e:
    import traceback
    print(f"\n❌ ERREUR: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)

finally:
    db.close()
