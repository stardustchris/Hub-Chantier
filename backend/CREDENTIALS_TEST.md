# Credentials de test - Hub Chantier

## 📝 Utilisateurs créés

### 1. Utilisateur Test (recommandé)
- **Email**: `test@hubchantier.fr`
- **Mot de passe**: `test123`
- **Rôle**: `admin`
- **Créé le**: 2026-01-28 22:03
- **Hash bcrypt vérifié**: ✅

### 2. Utilisateur Admin
- **Email**: `admin@hubchantier.fr`
- **Mot de passe**: `Password123!`
- **Rôle**: `admin`
- **Note**: Hash généré avec bcrypt.gensalt(rounds=12)

### 3. Utilisateur Conducteur
- **Email**: `conducteur@hubchantier.fr`
- **Mot de passe**: Voir admin (même hash initialement)
- **Rôle**: `conducteur`

## 🔧 Scripts utiles

### Créer un hash bcrypt
```bash
cd backend
python3 create_user_hash.py
```

### Tester l'API
```bash
cd backend
python3 test_full_flow.py
```

## ⚠️ Problèmes connus

### Rate Limiting
Le backend a un rate limiting sur `/api/auth/login`. Après plusieurs échecs:
```
{"detail":"Too many failed attempts. Try again in X seconds."}
```

**Solution**: Attendre le délai indiqué.

### Authentification échoue (401)
Si vous obtenez `{"detail":"Email ou mot de passe incorrect"}` alors que les credentials sont corrects, vérifiez:

1. Que l'utilisateur existe:
```bash
sqlite3 backend/hub_chantier.db "SELECT id, email, is_active, role FROM users"
```

2. Que le hash est correct:
```python
import bcrypt
password = "test123"
stored_hash = "$2b$12$..." # copier depuis la base
print(bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")))
```

3. Que le backend a bien redémarré après les changements de modèles

## 📊 Données de test

### Chantier
- **ID**: 1
- **Code**: A001
- **Nom**: Residence Les Jardins
- **Adresse**: 15 Avenue des Fleurs, 75001 Paris

### Dossier
- **ID**: 1
- **Nom**: Plans
- **Type**: 01_plans
- **Niveau d'accès**: compagnon
- **Chantier ID**: 1

## 🔍 Debugging

### Vérifier que le backend fonctionne
```bash
curl http://localhost:8000/health
```

### Tester le login manuellement
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@hubchantier.fr&password=test123"
```

### Voir les logs backend
Le backend utilise uvicorn avec `--reload`. Les logs apparaissent dans le terminal où il a été lancé.
