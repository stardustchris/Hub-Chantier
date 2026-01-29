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
