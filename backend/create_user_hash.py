#!/usr/bin/env python3
"""Génère un hash bcrypt pour un mot de passe."""

import bcrypt
import sqlite3

# Mot de passe simple: "Password123!"
password = "Password123!"

# Générer le hash exactement comme le fait BcryptPasswordService
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
hash_str = hashed.decode("utf-8")

print(f"Mot de passe: {password}")
print(f"Hash généré: {hash_str}")

# Mettre à jour l'utilisateur admin
conn = sqlite3.connect("hub_chantier.db")
cursor = conn.cursor()

cursor.execute(
    "UPDATE users SET password_hash = ? WHERE email = ?",
    (hash_str, "admin@hubchantier.fr")
)
conn.commit()

print(f"\n✅ Utilisateur admin mis à jour!")
print(f"   Email: admin@hubchantier.fr")
print(f"   Mot de passe: {password}")

conn.close()
