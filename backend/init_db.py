from sqlalchemy import create_engine, inspect
from shared.infrastructure.database_base import Base

# Import models
from modules.auth.infrastructure.persistence.user_model import UserModel
from modules.auth.infrastructure.persistence.api_key_model import APIKeyModel
from shared.infrastructure.webhooks.models import WebhookModel, WebhookDeliveryModel
from modules.chantiers.infrastructure.persistence.chantier_model import ChantierModel
from modules.dashboard.infrastructure.persistence.models import PostModel, CommentModel, LikeModel
from modules.documents.infrastructure.persistence.models import DossierModel, DocumentModel
from modules.planning.infrastructure.persistence.affectation_model import AffectationModel
from modules.planning.infrastructure.persistence.besoin_charge_model import BesoinChargeModel
from modules.pointages.infrastructure.persistence.models import PointageModel, FeuilleHeuresModel, VariablePaieModel
from modules.taches.infrastructure.persistence.tache_model import TacheModel
from modules.taches.infrastructure.persistence.template_modele_model import TemplateModeleModel, SousTacheModeleModel
from modules.taches.infrastructure.persistence.feuille_tache_model import FeuilleTacheModel
from modules.formulaires.infrastructure.persistence import (
    TemplateFormulaireModel,
    ChampTemplateModel,
    FormulaireRempliModel,
    ChampRempliModel,
    PhotoFormulaireModel,
)
from modules.financier.infrastructure.persistence.models import (
    BudgetModel,
    LotBudgetaireModel,
    AchatModel,
    FournisseurModel,
    SituationTravauxModel,
    FactureClientModel,
)
from modules.logistique.infrastructure.persistence.models import RessourceModel, ReservationModel
# Event logs and audit logs will be created via migrations if needed

engine = create_engine("sqlite:///hub_chantier.db", echo=False)
Base.metadata.create_all(engine)

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"✅ {len(tables)} tables créées!")
for table in sorted(tables):
    print(f"  - {table}")
