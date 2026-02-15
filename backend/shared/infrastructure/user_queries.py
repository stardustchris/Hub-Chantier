"""Shared user query helpers to avoid cross-module Model imports.

These helpers use raw SQL to look up user data, so that modules like
dashboard, formulaires, and notifications do not need to import
modules.auth.infrastructure.persistence.UserModel directly.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, bindparam
from typing import Optional


def get_user_display_name(db: Session, user_id: int) -> Optional[str]:
    """Get user display name without importing UserModel."""
    result = db.execute(
        text("SELECT prenom, nom FROM users WHERE id = :id"),
        {"id": user_id},
    ).fetchone()
    if result:
        return f"{result[0]} {result[1]}"
    return None


def get_user_basic_info(db: Session, user_id: int) -> Optional[dict]:
    """Get basic user info without importing UserModel."""
    result = db.execute(
        text(
            "SELECT id, prenom, nom, email, role, couleur, metiers, photo_profil, "
            "type_utilisateur, is_active "
            "FROM users WHERE id = :id AND deleted_at IS NULL"
        ),
        {"id": user_id},
    ).fetchone()
    if result:
        # metiers is now a JSON array, extract first element if exists
        metiers = result[6]
        metier = None
        if metiers:
            import json
            try:
                metiers_list = json.loads(metiers) if isinstance(metiers, str) else metiers
                if metiers_list and len(metiers_list) > 0:
                    metier = metiers_list[0]
            except (json.JSONDecodeError, TypeError):
                pass

        return {
            "id": result[0],
            "prenom": result[1],
            "nom": result[2],
            "email": result[3],
            "role": result[4],
            "couleur": result[5],
            "metier": metier,
            "photo_profil": result[7],
            "type_utilisateur": result[8],
            "is_active": bool(result[9]),
        }
    return None


def get_users_basic_info_by_ids(db: Session, user_ids: list[int]) -> dict[int, dict]:
    """Get basic user info for multiple users without importing UserModel.

    Returns:
        Dict mapping user_id -> user info dict.
    """
    if not user_ids:
        return {}

    rows = db.execute(
        text(
            "SELECT id, prenom, nom, email, role, couleur, metiers, photo_profil, "
            "type_utilisateur, is_active "
            "FROM users WHERE id IN :ids"
        ).bindparams(bindparam("ids", expanding=True)),
        {"ids": list(set(user_ids))},
    ).fetchall()

    import json
    result: dict[int, dict] = {}
    for row in rows:
        # metiers is now a JSON array, extract first element if exists
        metiers = row[6]
        metier = None
        if metiers:
            try:
                metiers_list = json.loads(metiers) if isinstance(metiers, str) else metiers
                if metiers_list and len(metiers_list) > 0:
                    metier = metiers_list[0]
            except (json.JSONDecodeError, TypeError):
                pass

        result[row[0]] = {
            "id": row[0],
            "prenom": row[1],
            "nom": row[2],
            "email": row[3],
            "role": row[4],
            "couleur": row[5],
            "metier": metier,
            "photo_profil": row[7],
            "type_utilisateur": row[8],
            "is_active": bool(row[9]),
        }
    return result


def count_active_users(db: Session) -> int:
    """Count total active users without importing UserModel."""
    result = db.execute(
        text("SELECT COUNT(id) FROM users WHERE is_active = true"),
    ).scalar()
    return result or 0


def count_active_users_by_metier(db: Session) -> dict[str, int]:
    """Count active users grouped by metier without importing UserModel.

    Note: Now returns counts by first metier in the metiers array.

    Returns:
        Dict mapping metier -> count (metier can be None).
    """
    # Since metiers is now a JSON array, we need to extract the first element
    # This query uses SQLite json_extract to get the first element
    rows = db.execute(
        text(
            "SELECT json_extract(metiers, '$[0]') as metier, COUNT(id) FROM users "
            "WHERE is_active = true GROUP BY metier"
        ),
    ).fetchall()
    return {row[0]: row[1] for row in rows}


def count_active_users_not_in_ids(db: Session, exclude_user_ids: list[int]) -> int:
    """Count active users NOT in the given ID list.

    Used to find users without affectations for a given period.

    Args:
        db: Database session.
        exclude_user_ids: User IDs to exclude.

    Returns:
        Count of active users not in the list.
    """
    if not exclude_user_ids:
        return count_active_users(db)

    result = db.execute(
        text(
            "SELECT COUNT(id) FROM users "
            "WHERE is_active = true AND id NOT IN :ids"
        ).bindparams(bindparam("ids", expanding=True)),
        {"ids": list(set(exclude_user_ids))},
    ).scalar()
    return result or 0


def get_metier_for_user_ids(db: Session, user_ids: list[int]) -> dict[int, Optional[str]]:
    """Get metier for a list of user IDs.

    Note: Returns the first metier from the metiers array.

    Returns:
        Dict mapping user_id -> metier (or None).
    """
    if not user_ids:
        return {}

    rows = db.execute(
        text(
            "SELECT id, json_extract(metiers, '$[0]') FROM users WHERE id IN :ids"
        ).bindparams(bindparam("ids", expanding=True)),
        {"ids": list(set(user_ids))},
    ).fetchall()
    return {row[0]: row[1] for row in rows}


def find_user_id_by_email_or_name(db: Session, identifier: str) -> Optional[int]:
    """Find a user ID by email prefix or name match, without importing UserModel.

    Args:
        db: Database session.
        identifier: Email prefix or (partial) name to search.

    Returns:
        User ID or None.
    """
    result = db.execute(
        text(
            "SELECT id FROM users WHERE "
            "email ILIKE :email_pat OR nom ILIKE :name_pat OR prenom ILIKE :name_pat "
            "LIMIT 1"
        ),
        {"email_pat": f"{identifier}%", "name_pat": f"%{identifier}%"},
    ).fetchone()
    return result[0] if result else None
