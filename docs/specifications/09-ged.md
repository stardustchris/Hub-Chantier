## 9. GESTION DOCUMENTAIRE (GED)

### 9.1 Vue d'ensemble

Le module Documents offre une gestion documentaire complete avec arborescence par dossiers numerotes, controle d'acces granulaire par role et nominatif, et synchronisation offline automatique des plans pour consultation terrain.

### 9.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| GED-01 | Onglet Documents integre | Dans chaque fiche chantier | ✅ |
| GED-02 | Arborescence par dossiers | Organisation hierarchique numerotee | ✅ |
| GED-03 | Tableau de gestion | Vue liste avec metadonnees (taille, date, auteur) | ✅ |
| GED-04 | Role minimum par dossier | Compagnon / Chef / Conducteur / Admin | ✅ |
| GED-05 | Autorisations specifiques | Permissions nominatives additionnelles | ✅ |
| GED-06 | Upload multiple | Jusqu'a 10 fichiers simultanes | ✅ |
| GED-07 | Taille max 10 Go | Par fichier individuel | ✅ |
| GED-08 | Zone Drag & Drop | Glisser-deposer intuitif | ✅ |
| GED-09 | Barre de progression | Affichage % upload en temps reel | ✅ |
| GED-10 | Selection droits a l'upload | Roles + Utilisateurs nominatifs | ✅ |
| GED-11 | Transfert auto depuis ERP | Synchronisation Costructor/Graneet | ⏳ Infra |
| GED-12 | Formats supportes | PDF, Images (PNG/JPG), XLS/XLSX, DOC/DOCX, Videos | ✅ |
| GED-13 | Actions Editer/Supprimer | Gestion complete des fichiers | ✅ |
| GED-14 | Consultation mobile | Visualisation sur application (responsive) | ✅ |
| GED-15 | Synchronisation Offline | Plans telecharges automatiquement | ⏳ Infra |
| GED-16 | Telechargement groupe ZIP | Selection multiple + archive ZIP a telecharger | ✅ |
| GED-17 | Previsualisation integree | Visionneuse PDF/images/videos dans l'application | ✅ |

**Module COMPLET** - Backend + Frontend implementes (15/17 fonctionnalites, 2 en attente infra)

**Note technique (29/01/2026)** : Refactorisation et corrections du téléchargement de documents :
- ✅ Clean Architecture respectée : use case retourne BinaryIO, routes utilisent le contrôleur
- ✅ Frontend : Token CSRF lu depuis le cookie, gestion blob response avec `responseType: 'blob'`
- ✅ Backend : Route `/download-zip` corrigée, téléchargements individuels et ZIP fonctionnels
- Tests manuels validés : 120KB PDF téléchargé, 103KB ZIP avec 2 documents

### 9.3 Niveaux d'acces

| Role minimum | Qui peut voir | Cas d'usage |
|--------------|---------------|-------------|
| Compagnon/Sous-Traitant | Tous utilisateurs du chantier | Plans d'execution, consignes securite |
| Chef de Chantier | Chefs + Conducteurs + Admin | Documents techniques sensibles |
| Conducteur | Conducteurs + Admin uniquement | Contrats, budgets, planning macro |
| Administrateur | Admin uniquement | Documents confidentiels, RH |

### 9.4 Arborescence type

| N° | Dossier | Contenu type |
|----|---------|--------------|
| 01 | Plans | Plans d'execution, plans beton, reservations |
| 02 | Documents administratifs | Marches, avenants, OS, situations |
| 03 | Securite | PPSPS, plan de prevention, consignes |
| 04 | Qualite | Fiches techniques, PV essais, autocontroles |
| 05 | Photos | Photos chantier par date/zone |
| 06 | Comptes-rendus | CR reunions, CR chantier |
| 07 | Livraisons | Bons de livraison, bordereaux |

---