"""Exemple de récepteur de webhooks Flask."""

from flask import Flask, request, jsonify
from hub_chantier import verify_webhook_signature

app = Flask(__name__)

# Secret reçu lors de la création du webhook
# À stocker dans les variables d'environnement en production
WEBHOOK_SECRET = "your_webhook_secret_here"


@app.route("/webhooks/hub-chantier", methods=["POST"])
def handle_webhook():
    """
    Handler pour les webhooks Hub Chantier.

    Vérifie la signature HMAC et traite les événements.
    """
    # Récupérer le payload et la signature
    payload = request.json
    signature = request.headers.get("X-Hub-Chantier-Signature")

    # Vérifier la signature HMAC
    if not verify_webhook_signature(payload, signature, WEBHOOK_SECRET):
        print("❌ Signature invalide - webhook rejeté")
        return jsonify({"error": "Invalid signature"}), 401

    # Extraire les informations de l'événement
    event_type = payload.get("event")
    data = payload.get("data")
    timestamp = payload.get("timestamp")

    print(f"✅ Webhook reçu : {event_type} à {timestamp}")

    # Traiter selon le type d'événement
    if event_type == "chantier.created":
        handle_chantier_created(data)

    elif event_type == "chantier.updated":
        handle_chantier_updated(data)

    elif event_type == "affectation.created":
        handle_affectation_created(data)

    elif event_type == "affectation.updated":
        handle_affectation_updated(data)

    else:
        print(f"⚠️  Événement non géré : {event_type}")

    return jsonify({"status": "ok"}), 200


def handle_chantier_created(data):
    """Traite la création d'un chantier."""
    print(f"📋 Nouveau chantier : {data['nom']} (ID {data['id']})")
    print(f"   Adresse : {data['adresse']}")
    print(f"   Statut : {data['statut']}")

    # Exemples d'actions possibles:
    # - Envoyer notification Slack
    # - Créer dossier dans système de fichiers
    # - Synchroniser avec ERP externe
    # - Envoyer email au conducteur


def handle_chantier_updated(data):
    """Traite la modification d'un chantier."""
    print(f"📝 Chantier modifié : {data['nom']} (ID {data['id']})")


def handle_affectation_created(data):
    """Traite la création d'une affectation."""
    print(f"👷 Nouvelle affectation : User {data['utilisateur_id']} → Chantier {data['chantier_id']}")
    print(f"   Date : {data['date']}")
    print(f"   Horaires : {data.get('heure_debut', 'N/A')} - {data.get('heure_fin', 'N/A')}")

    # Exemples d'actions possibles:
    # - Envoyer SMS à l'utilisateur
    # - Créer événement dans calendrier externe
    # - Notifier le conducteur de travaux


def handle_affectation_updated(data):
    """Traite la modification d'une affectation."""
    print(f"📅 Affectation modifiée : ID {data['id']}")


if __name__ == "__main__":
    print("🚀 Démarrage du serveur webhook sur http://localhost:5000")
    print("📡 Endpoint : http://localhost:5000/webhooks/hub-chantier")
    print()
    print("Pour tester avec ngrok:")
    print("  1. ngrok http 5000")
    print("  2. Copier l'URL HTTPS (ex: https://abc123.ngrok.io)")
    print("  3. Créer webhook dans Hub Chantier avec URL : https://abc123.ngrok.io/webhooks/hub-chantier")
    print()

    app.run(host="0.0.0.0", port=5000, debug=True)
