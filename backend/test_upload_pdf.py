#!/usr/bin/env python3
"""Test de l'upload d'un PDF après correction du bug DocumentDTO."""

import requests

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TEST UPLOAD PDF - Après correction DocumentDTO")
print("=" * 60)

# 1. Login
print("\n📝 1. CONNEXION")
print("-" * 40)
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    data={"username": "test@test.fr", "password": "Test123!"}
)

if response.status_code != 200:
    print(f"❌ Login échoué ({response.status_code})")
    print(f"   Réponse: {response.text}")
    exit(1)

data = response.json()
token = data["access_token"]
user = data["user"]

print(f"✅ Login réussi!")
print(f"   Utilisateur: {user['prenom']} {user['nom']}")

headers = {"Authorization": f"Bearer {token}"}

# 2. Upload du PDF
print("\n⬆️  2. UPLOAD DU PDF")
print("-" * 40)

with open("test_document.pdf", "rb") as f:
    files = {
        "file": ("test_document.pdf", f, "application/pdf")
    }

    response = requests.post(
        f"{BASE_URL}/api/documents/dossiers/1/documents?chantier_id=1",
        headers=headers,
        files=files
    )

print(f"Status: {response.status_code}")

if response.status_code == 201:
    result = response.json()
    print(f"✅ Upload réussi!")
    print(f"   Document ID: {result['id']}")
    print(f"   Nom: {result['nom']}")
    print(f"   Taille: {result['taille_formatee']}")
    print(f"   Type: {result['type_document']}")
    print(f"   Mime: {result['mime_type']}")

    doc_id = result['id']

    # 3. Test téléchargement
    print("\n🔽 3. TÉLÉCHARGEMENT")
    print("-" * 40)
    response = requests.get(
        f"{BASE_URL}/api/documents/{doc_id}/download",
        headers=headers,
        stream=True
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        content_length = response.headers.get('content-length', 'unknown')
        content_type = response.headers.get('content-type', 'unknown')
        content_disp = response.headers.get('content-disposition', 'unknown')

        print(f"✅ Téléchargement OK!")
        print(f"   Content-Length: {content_length} bytes")
        print(f"   Content-Type: {content_type}")
        print(f"   Content-Disposition: {content_disp}")

        # Sauvegarder pour vérifier
        with open("downloaded_test.pdf", "wb") as f:
            f.write(response.content)

        print(f"✅ Fichier sauvegardé: downloaded_test.pdf")
    else:
        print(f"❌ Échec téléchargement")
        print(f"   Réponse: {response.text[:200]}")

else:
    print(f"❌ Erreur upload")
    print(f"   Réponse: {response.text[:500]}")

print("\n" + "=" * 60)
print("FIN DES TESTS")
print("=" * 60)
