"""Shared chantier query helpers to avoid cross-module Model imports.

These helpers use raw SQL so that modules like formulaires do not need
to import modules.chantiers.infrastructure.persistence.ChantierModel.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional


def get_chantier_basic_info(db: Session, chantier_id: int) -> Optional[dict]:
    """Get basic chantier info without importing ChantierModel."""
    result = db.execute(
        text("SELECT id, nom FROM chantiers WHERE id = :id"),
        {"id": chantier_id},
    ).fetchone()
    if result:
        return {"id": result[0], "nom": result[1]}
    return None


def get_chantiers_actifs(db: Session, search: Optional[str] = None) -> list[dict]:
    """Get active chantiers (ouvert, en_cours) without importing ChantierModel.

    Args:
        db: Database session.
        search: Optional search term for nom/code.

    Returns:
        List of dicts with id, code, nom, couleur, heures_estimees.
    """
    if search:
        search_term = f"%{search}%"
        rows = db.execute(
            text(
                "SELECT id, code, nom, couleur, heures_estimees FROM chantiers "
                "WHERE statut IN ('ouvert', 'en_cours') AND deleted_at IS NULL "
                "AND (nom ILIKE :search OR code ILIKE :search) "
                "ORDER BY code"
            ),
            {"search": search_term},
        ).fetchall()
    else:
        rows = db.execute(
            text(
                "SELECT id, code, nom, couleur, heures_estimees FROM chantiers "
                "WHERE statut IN ('ouvert', 'en_cours') AND deleted_at IS NULL "
                "ORDER BY code"
            ),
        ).fetchall()

    return [
        {
            "id": r[0],
            "code": r[1],
            "nom": r[2],
            "couleur": r[3] or "#3498DB",
            "heures_estimees": r[4] or 0.0,
        }
        for r in rows
    ]


def get_chantier_by_id_dict(db: Session, chantier_id: int) -> Optional[dict]:
    """Get a single chantier by ID without importing ChantierModel.

    Returns:
        Dict with id, code, nom, couleur, heures_estimees or None.
    """
    row = db.execute(
        text(
            "SELECT id, code, nom, couleur, heures_estimees FROM chantiers "
            "WHERE id = :id AND deleted_at IS NULL"
        ),
        {"id": chantier_id},
    ).fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "code": row[1],
        "nom": row[2],
        "couleur": row[3] or "#3498DB",
        "heures_estimees": row[4] or 0.0,
    }


def get_chantiers_basic_info_by_ids(db: Session, chantier_ids: list[int]) -> dict[int, dict]:
    """Get basic chantier info for multiple chantiers.

    Returns:
        Dict mapping chantier_id -> chantier info dict.
    """
    if not chantier_ids:
        return {}

    params = {f"id_{i}": cid for i, cid in enumerate(set(chantier_ids))}
    placeholders = ", ".join(f":{k}" for k in params)

    rows = db.execute(
        text(f"SELECT id, nom FROM chantiers WHERE id IN ({placeholders})"),
        params,
    ).fetchall()

    return {row[0]: {"id": row[0], "nom": row[1]} for row in rows}
