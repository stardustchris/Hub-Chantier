"""Base SQLAlchemy partagée pour tous les modules."""

from sqlalchemy.orm import declarative_base

# Base unique partagée par tous les modules
# Cela permet aux ForeignKeys de fonctionner entre modules
Base = declarative_base()
