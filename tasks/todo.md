# Plan d'action ConfigurationEntreprise — Phases 0 à 4

> Source : synthese confrontation inter-agents (audit session 2026-02-11)

---

## Phase 0 — Immediat (0.5j)

- [x] 0.1 Bandeau avertissement admin → OBSOLETE (config connectee aux calculs)
- [x] 0.2 Corriger 11 findings audit (TYPE-001, VAL-001/002, EDGE-001/002/003, FLUX-001/002/003, MIG-001/002)
- [x] 0.3 Tests non-regression module ConfigurationEntreprise (13 tests unit entity + use cases)

## Phase 1 — ConfigurationService (1.5j)

- [x] 1.1 Creer ConfigurationEntrepriseRepository + SQLAlchemy impl
- [x] 1.2 Brancher dashboard_use_cases sur config DB (coeff_frais_generaux)
- [x] 1.3 Brancher pnl_use_cases sur config DB (coeff_frais_generaux)
- [x] 1.4 Brancher bilan_cloture_use_cases sur config DB (coeff_frais_generaux)
- [x] 1.5 Brancher consolidation_use_cases sur config DB (coeff_frais_generaux)
- [x] 1.6 Brancher sqlalchemy_cout_main_oeuvre_repository sur config DB (charges, HS1, HS2)
- [x] 1.7 Fix default devis models.py 12% → 19% + migration
- [x] 1.8 Supprimer constantes hardcodees → conservees comme fallbacks (correct)

## Phase 2 — Integration devis + tests (1j)

- [x] 2.1 DevisForm frontend charge coeff depuis API config
- [x] 2.2 Tests integration : config DB → dashboard → verifier calcul FG (22 tests)
- [x] 2.3 Tests integration : config DB → MO → verifier calcul charges
- [x] 2.4 Tests integration : config DB → devis → verifier coeff par defaut + fallback

## Phase 3 — Cache + nettoyage + alertes (1j)

- [x] 3.1 Cache config en memoire TTL 300s (time.monotonic, invalidation sur save)
- [x] 3.2 Alerte revalidation 180j : stale_warning backend + bandeau jaune frontend
- [x] 3.3 Nettoyage emplacements residuels : fix Decimal("19") hardcode dans devis_routes + devis_dtos

## Phase 4 — Fonctionnalites avancees (3j, mois 2)

- [ ] 4.1 Coefficient productivite (champ devis, impact calcul)
- [ ] 4.2 Granularite charges par categorie (ouvrier/ETAM/cadre)
- [ ] 4.3 Alertes budget (seuils configurables)
- [ ] 4.4 Champ commentaire libre devis (en attendant coeff productivite)

---

## Decisions

- Charges patronales : Greg a decide 1.45 (Finance proposait 1.57, Greg assume le risque)
- Coefficient productivite : Phase 4 (Conducteur voulait Phase 2, groupe a tranche Phase 4)
- Estimation : 4j senior dev Phases 0-3, +3j Phase 4

## Garde-fous post-deploiement

- [ ] Recalcul 5 derniers devis pour mesurer ecart reel (Finance)
- [ ] Alerte Greg si ecart > 5% (Finance)
- [ ] Revalidation semestrielle coefficients par expert-comptable (Greg)

---

## Historique commits

| Commit | Description |
|--------|-------------|
| `52263d4` | feat: page Parametres Entreprise (CRUD config) |
| `5c942bd` | fix: connecter ConfigurationEntreprise aux calculs financiers |
| `0ad8673` | fix: corriger VAL-001/002, EDGE-001/002/003 |
| `18587b1` | feat: cache TTL 5min + alerte 180j + 13 tests unitaires |
| `942824f` | test: 22 tests integration config DB → calculs financiers |
| `6e7bc18` | fix: lire coefficient_frais_generaux depuis config DB dans module devis |

---
---

# Plan — Synchronisation automatique des heures validées vers Costructor

> Session 2026-10-05. Statut : **implémenté et testé en réel (non commité)**.

## Faits établis (testés sur le compte de démo Costructor)

- `POST /external/v1/timesheet_entries` crée une saisie ; `DELETE /{id}` la supprime ; `PATCH`/`PUT` refusés (405).
- Champs : `user` (usr_…), `type` (work | travel | packed_lunch), `day` (AAAA-MM-JJ), `project` (pj_…), `startTime`/`endTime` (HH:MM), `zone` (z1a, z5… facultatif), `notes`.
- **Début et fin obligatoires** pour le travail : une durée seule est refusée (400).
- **Aucune pause déduite** : Costructor compte l'amplitude fin − début.
- **Aucune idempotence** : renvoyer la même saisie crée un doublon.
- Côté Hub Chantier : un pointage ne stocke que des **durées**, pas d'horaires.
- Côté Hub Chantier : les événements de domaine publiés par les use cases de validation **n'atteignent aucun abonné** (bus asynchrone appelé sans `await`) → on ne branche pas la synchro dessus.

## Règles métier retenues

- Horaires de référence : **8h00 → 16h00, repas 12h00 → 13h00** (7h/jour, 35h/semaine), configurables.
- Une journée = **deux saisies** encadrant le repas, total = heures validées exactes :
  - 7h → 08:00-12:00 + 13:00-16:00
  - 10h → 08:00-12:00 + 13:00-19:00
  - ≤ 4h → une seule saisie, 08:00-(08:00+durée)
  - 0h → rien n'est envoyé
- **Confirmé** : heures sup déclenchées au-delà de **35h/semaine** → chaque jour est envoyé avec son total, sans qualifier d'heures sup (calcul hebdomadaire laissé à la paie).
- Hypothèse (à confirmer) : correspondance par **identifiant Costructor saisi par l'admin** sur la fiche compagnon et la fiche chantier ; sans identifiant → pointage « ignoré », visible par l'admin.
- Hypothèse (à confirmer) : **v1 = heures de travail seulement** ; paniers et déplacements en v2 (la zone n'existe pas encore).

## Étapes

- [x] 1. Fonction pure de découpage durée → créneaux (matin / après-midi), configurable, testée en premier (cas 0h, 3h, 4h, 7h, 7h30, 10h)
- [x] 2. Port applicatif `SynchronisationPaieExternePort` (module pointages) — pas de dépendance à Costructor dans le domaine
- [x] 3. Client Costructor dans `pointages/infrastructure/paie_externe/` (seul utilisateur : pas de connecteur partagé)
- [x] 4. Table `costructor_sync` : pointage_id unique, ids Costructor créés, statut (envoyé / erreur / ignoré), message, nb tentatives, dates → **anti-doublon et reprise**
- [x] 5. Table `correspondances_paie_externe` (au lieu de colonnes sur `users`/`chantiers` : pas de couplage avec les autres modules)
- [x] 6. Déclenchement **explicite après validation** (unitaire, en lot, auto-validation à la soumission, **et création par admin/conducteur/chef**) ; un échec Costructor ne bloque jamais la validation
- [x] 7. Endpoints admin : statut, suivis, relance, **envoi explicite** (heures validées avant activation), correspondances
- [x] 8. Configuration par variables d'environnement : `COSTRUCTOR_API_KEY`, `COSTRUCTOR_SYNC_ENABLED` (désactivé par défaut), horaires de référence
- [ ] 9. Écran de saisie des correspondances (frontend) — **reporté** : dépend du choix de correspondance (hypothèse ouverte)
- [x] 10. Test de bout en bout sur le compte de démo (validation → saisies créées → relecture → nettoyage), puis 4 validations et PR

## Hors périmètre (signalé)

- Bug du bus d'événements des pointages (événements perdus) — tâche séparée.
- `HeuresValidatedEvent` tronque les minutes (7h30 → 7.0) — tâche séparée.
- Paniers repas et déplacements (v2, après ajout de la zone).

## Résultats (2026-10-05)

- Tests : 5533 passent (+67 nouveaux) ; couverture des nouveaux fichiers 92-100 %.
- Bout en bout sur le compte de démo, tous chemins vérifiés :
  - création par admin, création par chef, validation en lot par un chef (compagnon : brouillon → soumis → validé) ;
  - 7h → 08:00-12:00 + 13:00-16:00 ; 7h30 + 1h → 08:00-12:00 + 13:00-17:30 (8h30) ;
  - anti-doublon : renvoi de 4 pointages → « déjà envoyés », 26 saisies avant comme après ;
  - chantier sans correspondance → « ignoré » avec message, puis envoyé à la relance après ajout.
- Limitation de débit Costructor découverte (429 après ~10 appels) : attente progressive 2/4/8/16 s ; rafale réelle de 12 créations + 12 suppressions passée sans échec.
- Nettoyage : 0 saisie de test restante chez Costructor (18, comme avant) ; pointages et correspondances de test supprimés ; synchronisation redésactivée.

## Découvertes en cours de route

- Deux chemins de validation imprévus : la création par admin/conducteur/chef valide d'emblée (`create_pointage.py`). Branché sur le statut renvoyé, pas sur le rôle.
- Les heures validées **avant** l'activation ne partiraient jamais (la relance ne couvre que erreurs/ignorés) → route d'envoi explicite.

## Mise en service

1. Dans `.env` (jamais commité) : `COSTRUCTOR_SYNC_ENABLED=true`, `COSTRUCTOR_API_KEY=...`
2. Déclarer les correspondances : `PUT /api/paie-externe/correspondances` (admin)
3. Optionnel : envoyer l'historique validé via `POST /api/paie-externe/synchronisations/envoyer`

