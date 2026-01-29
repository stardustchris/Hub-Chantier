"""Exemple quickstart Hub Chantier SDK."""

from hub_chantier import HubChantierClient

# Initialiser le client
# Remplacez par votre vraie clé API depuis Paramètres > Clés API
client = HubChantierClient(api_key="hbc_your_api_key_here")

# Exemple 1: Lister les chantiers en cours
print("=== Chantiers en cours ===")
chantiers = client.chantiers.list(status="en_cours", limit=10)
for chantier in chantiers:
    print(f"- {chantier['nom']} ({chantier['adresse']})")

# Exemple 2: Créer un nouveau chantier
print("\n=== Créer un chantier ===")
nouveau_chantier = client.chantiers.create(
    nom="Villa Caluire - Construction neuve",
    adresse="12 Rue de la République, 69300 Caluire-et-Cuire",
    statut="ouvert",
    couleur="#3B82F6",
    description="Construction d'une villa individuelle de 150m²",
)
print(f"✅ Chantier créé : ID {nouveau_chantier['id']}")

# Exemple 3: Créer une affectation
print("\n=== Créer une affectation ===")
affectation = client.affectations.create(
    utilisateur_id=5,  # ID de l'utilisateur à affecter
    chantier_id=int(nouveau_chantier["id"]),
    date="2026-01-30",
    heure_debut="08:00",
    heure_fin="17:00",
    note="Travaux de fondation",
)
print(f"✅ Affectation créée : ID {affectation['id']}")

# Exemple 4: Lister les affectations de la semaine
print("\n=== Affectations semaine du 20 au 26 janvier ===")
affectations = client.affectations.list(
    date_debut="2026-01-20", date_fin="2026-01-26"
)
print(f"Nombre d'affectations : {len(affectations)}")

# Exemple 5: Créer un webhook
print("\n=== Créer un webhook ===")
webhook = client.webhooks.create(
    url="https://myapp.example.com/webhooks/hub-chantier",
    events=["chantier.created", "affectation.created"],
    description="Webhook production - notifications chantiers",
)
print(f"✅ Webhook créé : {webhook['id']}")
print(f"⚠️  Secret à sauvegarder : {webhook['secret']}")

print("\n✅ Quickstart terminé avec succès!")
