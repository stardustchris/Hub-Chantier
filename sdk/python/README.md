# Hub Chantier Python SDK

SDK Python officiel pour [Hub Chantier API](https://hub-chantier.fr).

## Installation

```bash
pip install hub-chantier
```

## Démarrage Rapide

```python
from hub_chantier import HubChantierClient

# Initialiser client
client = HubChantierClient(api_key="hbc_your_api_key_here")

# Lister chantiers
chantiers = client.chantiers.list(status="en_cours")
for chantier in chantiers:
    print(f"{chantier['nom']} - {chantier['adresse']}")

# Créer chantier
nouveau_chantier = client.chantiers.create(
    nom="Villa Caluire",
    adresse="12 Rue de la République, 69300 Caluire"
)
print(f"Chantier créé : {nouveau_chantier['id']}")

# Créer affectation
client.affectations.create(
    utilisateur_id=5,
    chantier_id=int(nouveau_chantier['id']),
    date="2026-01-30",
    heure_debut="08:00",
    heure_fin="17:00"
)
```

## Authentification

Créez une clé API depuis l'interface web Hub Chantier (Paramètres > Clés API).

Les clés API ont le format `hbc_...` et doivent être gardées secrètes.

## Utilisation

### Chantiers

```python
# Lister
chantiers = client.chantiers.list(
    status="en_cours",
    conducteur_id=5,
    limit=50
)

# Créer
chantier = client.chantiers.create(
    nom="Rénovation Appartement Lyon 6",
    adresse="45 Avenue Foch, 69006 Lyon",
    statut="ouvert",
    couleur="#3B82F6",
    date_debut="2026-02-01"
)

# Récupérer
chantier = client.chantiers.get(42)

# Modifier
chantier = client.chantiers.update(42, statut="en_cours")

# Supprimer
client.chantiers.delete(42)
```

### Affectations (Planning)

```python
# Lister affectations sur une période
affectations = client.affectations.list(
    date_debut="2026-01-20",
    date_fin="2026-01-26",
    utilisateur_ids=[1, 2, 3]
)

# Créer affectation
affectation = client.affectations.create(
    utilisateur_id=5,
    chantier_id=42,
    date="2026-01-30",
    heure_debut="08:00",
    heure_fin="17:00",
    note="Travaux de fondation"
)

# Modifier
affectation = client.affectations.update(
    123,
    heure_debut="09:00"
)

# Supprimer
client.affectations.delete(123)
```

### Feuilles d'Heures

```python
# Lister
heures = client.heures.list(
    date_debut="2026-01-01",
    date_fin="2026-01-31"
)

# Créer
feuille = client.heures.create(
    utilisateur_id=5,
    chantier_id=42,
    date="2026-01-30",
    heures=8.0
)
```

### Documents (GED)

```python
# Lister documents d'un chantier
documents = client.documents.list(chantier_id=42)

# Lister documents d'un dossier
documents = client.documents.list(
    chantier_id=42,
    dossier_id=15
)

# Récupérer un document
document = client.documents.get(127)
```

### Webhooks

```python
# Créer un webhook
webhook = client.webhooks.create(
    url="https://myapp.com/webhooks/hub-chantier",
    events=["chantier.created", "affectation.created"],
    description="Production webhook"
)

# Sauvegarder le secret pour vérifier les signatures
webhook_secret = webhook['secret']

# Lister webhooks
webhooks = client.webhooks.list()

# Supprimer
client.webhooks.delete("webhook-uuid")
```

## Vérification Signatures Webhooks

Vérifiez l'authenticité des webhooks reçus avec HMAC-SHA256 :

```python
from flask import Flask, request
from hub_chantier import verify_webhook_signature

app = Flask(__name__)
WEBHOOK_SECRET = "votre_secret_webhook"

@app.route('/webhooks/hub-chantier', methods=['POST'])
def handle_webhook():
    payload = request.json
    signature = request.headers.get('X-Hub-Chantier-Signature')

    if not verify_webhook_signature(payload, signature, WEBHOOK_SECRET):
        return 'Invalid signature', 401

    event_type = payload['event']

    if event_type == 'chantier.created':
        # Traiter création chantier
        chantier = payload['data']
        print(f"Nouveau chantier : {chantier['nom']}")

    elif event_type == 'affectation.created':
        # Traiter création affectation
        affectation = payload['data']
        print(f"Nouvelle affectation : user {affectation['utilisateur_id']}")

    return 'OK', 200

if __name__ == '__main__':
    app.run(port=5000)
```

## Gestion d'Erreurs

```python
from hub_chantier import (
    HubChantierClient,
    AuthenticationError,
    RateLimitError,
    APIError
)

client = HubChantierClient(api_key="hbc_...")

try:
    chantier = client.chantiers.get(999)
except AuthenticationError:
    print("Clé API invalide ou expirée")
except RateLimitError as e:
    print(f"Rate limit dépassé. Reset à {e.reset_at}")
except APIError as e:
    print(f"Erreur API ({e.status_code}): {e}")
```

## Configuration

### Environnements

```python
# Production (défaut)
client = HubChantierClient(api_key="hbc_...")

# Sandbox
client = HubChantierClient(
    api_key="hbc_test_...",
    base_url="https://sandbox.hub-chantier.fr"
)

# Local
client = HubChantierClient(
    api_key="hbc_dev_...",
    base_url="http://localhost:8000"
)
```

### Timeout

```python
# Timeout custom (défaut: 30 secondes)
client = HubChantierClient(
    api_key="hbc_...",
    timeout=60  # 60 secondes
)
```

## Documentation

- [API Reference](https://docs.hub-chantier.fr/api-reference)
- [Exemples](https://docs.hub-chantier.fr/examples)
- [Changelog](https://docs.hub-chantier.fr/changelog)

## Support

- **Email** : support@hub-chantier.fr
- **Documentation** : https://docs.hub-chantier.fr
- **Status** : https://status.hub-chantier.fr

## Licence

MIT
