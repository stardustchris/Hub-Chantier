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
