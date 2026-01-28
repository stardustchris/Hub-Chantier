from sqlalchemy import create_engine, inspect
from shared.infrastructure.database_base import Base

# Import models
from modules.auth.infrastructure.persistence.user_model import UserModel
from modules.auth.infrastructure.persistence.api_key_model import APIKeyModel
from shared.infrastructure.webhooks.models import WebhookModel, WebhookDeliveryModel
from modules.chantiers.infrastructure.persistence.chantier_model import ChantierModel
from modules.dashboard.infrastructure.persistence.models import PostModel, CommentModel, LikeModel
from modules.documents.infrastructure.persistence.models import DossierModel, DocumentModel

engine = create_engine("sqlite:///hub_chantier.db", echo=False)
Base.metadata.create_all(engine)

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"✅ {len(tables)} tables créées!")
for table in sorted(tables):
    print(f"  - {table}")
