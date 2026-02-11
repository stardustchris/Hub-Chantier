# Audit Financier - Corrections

## P1 - Bloquantes (chiffres faux)

- [ ] P1-1: Frais generaux jamais repartis → auto-calcul ca_total_annee + config couts_fixes
- [ ] P1-2: CA incoherent Dashboard vs P&L → unifier source
- [ ] P1-3: "marge_estimee" trompeuse en fallback → renommer
- [ ] P1-4: Montants non arrondis (3 properties) → arrondir_montant()
- [ ] P1-5: CHECK SQL retenue 10% illegal → migration IN (0, 5)
- [ ] P1-6: float() dans calcul SQL MO → precision Decimal

## P2 - Graves (risques metier)

- [ ] P2-1: montant_avenants_ht modifiable directement → verrouiller DTO
- [ ] P2-2: Fiabilite marge trompeuse → condition cout_materiel > 0
- [ ] P2-3: version jamais incrementee → increment mutations
- [ ] P2-4: SituationTravaux cumule non valide → validation
- [ ] P2-5: P&L pas de filtre soft-delete factures → filtre defensif
- [ ] P2-6: CHECK SQL TVA trop permissif → valeurs discretes
- [ ] P2-7: CHECK SQL autoliquidation manquant → constraint
- [ ] P2-8: Validation retenue garantie sur FactureClient
- [ ] P2-9: quantite=0 avec debourses > 0 → guard clause
- [ ] P2-10: Arrondis manquants reste_a_depenser + marge_brute_ht

## Conformite

- [ ] C-3: Palier 50% heures sup >43h → +50% au lieu de +25%

## Frontend

- [ ] FE-1: Labels marge estimee vs calculee (back P1-3)
- [ ] FE-2: "N/D" ambigu → distinguer null vs 0%
- [ ] FE-3: Retenue garantie validation frontend
- [ ] FE-4: Labels Engage/Realise/Debourse coherents

---

# Page Parametres Entreprise (Admin Only)

## Contexte
- L'entite `ConfigurationEntreprise` existe (domain) mais ne contient que `couts_fixes_annuels` et `annee`
- La table SQL `configuration_entreprise` existe avec les memes champs
- Il n'y a PAS de modele SQLAlchemy, pas de repository, pas de use cases, pas de routes API, pas de page frontend
- Les coefficients financiers sont hardcodes dans `calcul_financier.py`
- Le guard `require_admin` existe deja (role == "admin")
- Le user veut que seul l'admin puisse modifier

## Plan d'implementation

### Backend - Domain Layer
- [ ] 1. Enrichir `ConfigurationEntreprise` : ajouter `coeff_frais_generaux`, `coeff_charges_patronales`, `coeff_heures_sup`, `coeff_heures_sup_2` avec valeurs par defaut actuelles
- [ ] 2. Creer interface `ConfigurationEntrepriseRepository` dans `domain/repositories/`

### Backend - Application Layer
- [ ] 3. Creer DTOs (`ConfigurationEntrepriseDTO`, `ConfigurationEntrepriseUpdateDTO`)
- [ ] 4. Creer use cases (`GetConfigurationUseCase`, `UpdateConfigurationUseCase`)

### Backend - Infrastructure Layer
- [ ] 5. Creer `ConfigurationEntrepriseModel` dans `models.py`
- [ ] 6. Creer `SQLAlchemyConfigurationEntrepriseRepository`
- [ ] 7. Migration SQL : ALTER TABLE ajouter les colonnes coefficients
- [ ] 8. Creer routes API (GET + PUT) dans `financier_routes.py`, protegees par `require_admin`
- [ ] 9. Ajouter dependencies (injection)

### Backend - Shared
- [ ] 10. Modifier `calcul_financier.py` : les fonctions acceptent les coefficients en parametre (avec fallback sur constantes)

### Frontend
- [ ] 11. Creer `ParametresEntreprisePage.tsx` : formulaire admin avec tous les parametres
- [ ] 12. Ajouter route `/parametres` dans `App.tsx`
- [ ] 13. Ajouter lien "Parametres" dans `Layout.tsx` (visible admin only)

### Validation
- [ ] 14. Build docker (api + frontend)
- [ ] 15. Test health + smoke test API

## Decisions architecturales

1. **Pas de nouveau module** : ConfigurationEntreprise reste dans le module `financier` (c'est de la config financiere)
2. **Pas de CRUD complet** : Seulement GET (lecture) + PUT (update). La config est creee par la migration SQL, pas par l'utilisateur
3. **Coefficients en parametres** : Les fonctions de `calcul_financier.py` gardent les constantes comme valeurs par defaut, mais acceptent des parametres pour override
4. **Acces admin uniquement** : `require_admin` (role == "admin") sur PUT. GET accessible admin + conducteur
