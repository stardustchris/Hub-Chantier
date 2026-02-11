# Plan d'action ConfigurationEntreprise — Phases 0 à 4

> Source : synthese confrontation inter-agents (audit session 2026-02-11)

---

## Phase 0 — Immediat (0.5j)

- [x] 0.1 Bandeau avertissement admin → OBSOLETE (config connectee aux calculs)
- [x] 0.2 Corriger 11 findings audit (TYPE-001, VAL-001/002, EDGE-001/002/003, FLUX-001/002/003, MIG-001/002)
- [ ] 0.3 Tests non-regression module ConfigurationEntreprise (unit + API)

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
- [ ] 2.2 Tests integration : config DB → dashboard → verifier calcul FG
- [ ] 2.3 Tests integration : config DB → MO → verifier calcul charges
- [ ] 2.4 Tests integration : config DB → devis → verifier coeff par defaut

## Phase 3 — Cache + nettoyage + alertes (1j)

- [ ] 3.1 Cache config en memoire (eviter requete DB a chaque calcul)
- [ ] 3.2 Alerte revalidation 180j : warning si config non mise a jour depuis 6 mois
- [ ] 3.3 Nettoyage emplacements residuels → audit montre 95% clean, verifier restant

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
