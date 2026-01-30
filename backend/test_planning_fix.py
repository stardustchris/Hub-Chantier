#!/usr/bin/env python3
"""Script de test pour vérifier que l'endpoint planning fonctionne après la correction."""

import requests
import sys
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"

def login():
    """Authentifie et retourne le token."""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={
            "username": "admin@greg-construction.fr",
            "password": "Admin123!"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)

    data = response.json()
    print(f"✅ Login successful!")
    return data["access_token"]


def test_planning(token):
    """Test l'endpoint planning."""
    today = date.today()
    date_debut = (today - timedelta(days=3)).isoformat()
    date_fin = (today + timedelta(days=3)).isoformat()

    print(f"\n🔍 Testing planning endpoint...")
    print(f"   Date range: {date_debut} to {date_fin}")

    response = requests.get(
        f"{BASE_URL}/api/planning/affectations",
        params={
            "date_debut": date_debut,
            "date_fin": date_fin
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Planning endpoint works!")
        print(f"   Affectations: {len(data.get('affectations', []))}")
        print(f"   Non-planifiés: {len(data.get('non_planifies', []))}")
        return True
    else:
        print(f"❌ Planning endpoint failed!")
        print(f"   Response: {response.text[:500]}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("TEST DE CORRECTION DU PROBLÈME PLANNING")
    print("="*60)

    token = login()
    success = test_planning(token)

    print("\n" + "="*60)
    if success:
        print("✅ TEST RÉUSSI - Le problème est corrigé!")
    else:
        print("❌ TEST ÉCHOUÉ - Le problème persiste")
    print("="*60)

    sys.exit(0 if success else 1)
