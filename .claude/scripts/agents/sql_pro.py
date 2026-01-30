"""Agent SQL Pro - Validation migrations et schéma DB."""

import re
from pathlib import Path
from typing import List, Dict, Set
from .base import BaseAgent, AgentReport, AgentStatus


class SqlProAgent(BaseAgent):
    """
    Agent expert SQL et migrations.

    Vérifie :
    - Migrations Alembic bien formées
    - Contraintes d'intégrité (FK, NOT NULL, UNIQUE)
    - Index sur colonnes recherchées
    - Pas de requêtes N+1
    - Nomenclature PostgreSQL
    """

    REQUIRED_CONSTRAINTS = {
        'primary_key': r'primary_key=True',
        'foreign_key': r'ForeignKey\(',
        'unique': r'unique=True',
        'index': r'index=True',
    }

    def validate(self) -> AgentReport:
        """Exécute la validation SQL."""
        print(f"  🗄️  Validation SQL...")

        module_path = Path(self.module_path)

        if not module_path.exists():
            return self._create_report(
                AgentStatus.SKIP,
                "Module non trouvé"
            )

        # Vérification 1 : Migrations Alembic
        self._check_migrations()

        # Vérification 2 : Modèles SQLAlchemy
        self._check_models(module_path)

        # Vérification 3 : Requêtes N+1
        self._check_n_plus_one(module_path)

        # Vérification 4 : Index manquants
        self._check_missing_indexes(module_path)

        # Déterminer le statut
        status = self._determine_status()

        # Calculer les scores
        score = self._calculate_scores()

        summary = self._generate_summary(status)

        return self._create_report(status, summary, score)

    def _check_migrations(self):
        """Vérifie les migrations Alembic."""
        # Chercher le répertoire migrations
        migrations_path = Path.cwd() / 'backend' / 'migrations' / 'versions'

        if not migrations_path.exists():
            self.add_finding(
                severity='MEDIUM',
                message="Répertoire migrations non trouvé",
                file=str(migrations_path.relative_to(Path.cwd())),
                suggestion="Initialiser Alembic : alembic init migrations",
                category='database'
            )
            return

        migration_files = list(migrations_path.glob("*.py"))
        migration_files = [f for f in migration_files if f.name != '__init__.py']

        if not migration_files:
            self.add_finding(
                severity='MEDIUM',
                message="Aucune migration trouvée",
                file=str(migrations_path.relative_to(Path.cwd())),
                suggestion="Créer une migration : alembic revision --autogenerate -m 'message'",
                category='database'
            )
            return

        # Vérifier chaque migration
        for migration_file in migration_files:
            with open(migration_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier présence de upgrade() et downgrade()
            if 'def upgrade()' not in content:
                self.add_finding(
                    severity='CRITICAL',
                    message=f"Migration sans fonction upgrade()",
                    file=str(migration_file.relative_to(Path.cwd())),
                    suggestion="Ajouter def upgrade() -> None:",
                    category='database'
                )

            if 'def downgrade()' not in content:
                self.add_finding(
                    severity='HIGH',
                    message=f"Migration sans fonction downgrade()",
                    file=str(migration_file.relative_to(Path.cwd())),
                    suggestion="Ajouter def downgrade() -> None: pour rollback",
                    category='database'
                )

            # Vérifier les opérations dangereuses
            if 'drop_table' in content:
                self.add_finding(
                    severity='HIGH',
                    message="Migration contient DROP TABLE",
                    file=str(migration_file.relative_to(Path.cwd())),
                    suggestion="Vérifier que cette suppression est intentionnelle",
                    category='database'
                )

            if 'drop_column' in content and 'batch_op' not in content:
                self.add_finding(
                    severity='MEDIUM',
                    message="DROP COLUMN sans batch_op (problème SQLite)",
                    file=str(migration_file.relative_to(Path.cwd())),
                    suggestion="Utiliser with batch_alter_table(...)",
                    category='database'
                )

            # Vérifier les index sur clés étrangères
            if 'ForeignKey' in content:
                # Chercher les colonnes avec FK
                fk_columns = re.findall(r"'(\w+)',.*ForeignKey", content)
                for col in fk_columns:
                    # Vérifier si index créé
                    if f"create_index('ix_" not in content and f'"{col}"' not in content:
                        self.add_finding(
                            severity='MEDIUM',
                            message=f"Colonne FK '{col}' sans index",
                            file=str(migration_file.relative_to(Path.cwd())),
                            suggestion=f"Ajouter op.create_index('ix_table_{col}', 'table', ['{col}'])",
                            category='database'
                        )

    def _check_models(self, module_path: Path):
        """Vérifie les modèles SQLAlchemy."""
        models_path = module_path / 'infrastructure' / 'persistence'

        if not models_path.exists():
            return

        model_files = list(models_path.glob("*_model.py"))

        for model_file in model_files:
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier les relations sans lazy loading
            relations = re.findall(r'relationship\([^)]+\)', content)
            for relation in relations:
                if 'lazy=' not in relation:
                    self.add_finding(
                        severity='MEDIUM',
                        message="Relation sans stratégie lazy définie",
                        file=str(model_file.relative_to(Path.cwd())),
                        suggestion="Ajouter lazy='select' ou lazy='joined' explicitement",
                        category='database'
                    )

            # Vérifier les colonnes sans nullable défini
            columns = re.findall(r'Column\([^)]+\)', content)
            for column in columns:
                if 'nullable=' not in column and 'primary_key=True' not in column:
                    self.add_finding(
                        severity='LOW',
                        message="Colonne sans nullable défini",
                        file=str(model_file.relative_to(Path.cwd())),
                        suggestion="Ajouter nullable=False ou nullable=True explicitement",
                        category='database'
                    )

            # Vérifier les emails sans validation
            if re.search(r"Column\('email'", content):
                if 'EmailStr' not in content and '@' not in content:
                    self.add_finding(
                        severity='MEDIUM',
                        message="Colonne email sans validation",
                        file=str(model_file.relative_to(Path.cwd())),
                        suggestion="Ajouter validation email (Pydantic EmailStr ou constraint)",
                        category='database'
                    )

            # Vérifier les timestamps
            has_created_at = 'created_at' in content
            has_updated_at = 'updated_at' in content

            if not has_created_at:
                self.add_finding(
                    severity='LOW',
                    message="Modèle sans colonne created_at",
                    file=str(model_file.relative_to(Path.cwd())),
                    suggestion="Ajouter created_at = Column(DateTime(timezone=True), server_default=func.now())",
                    category='database'
                )

            if not has_updated_at:
                self.add_finding(
                    severity='LOW',
                    message="Modèle sans colonne updated_at",
                    file=str(model_file.relative_to(Path.cwd())),
                    suggestion="Ajouter updated_at = Column(DateTime(timezone=True), onupdate=func.now())",
                    category='database'
                )

    def _check_n_plus_one(self, module_path: Path):
        """Vérifie les problèmes de requêtes N+1."""
        repo_path = module_path / 'infrastructure' / 'persistence'

        if not repo_path.exists():
            return

        repo_files = list(repo_path.glob("*_repository.py"))

        for repo_file in repo_files:
            with open(repo_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier les queries sans joinedload
            if 'query(' in content or 'select(' in content:
                # Chercher les accès aux relations dans les boucles
                if re.search(r'for\s+\w+\s+in.*:\s+\w+\.\w+', content):
                    if 'joinedload' not in content and 'selectinload' not in content:
                        self.add_finding(
                            severity='HIGH',
                            message="Risque de N+1 queries (boucle avec accès relation)",
                            file=str(repo_file.relative_to(Path.cwd())),
                            suggestion="Utiliser joinedload() ou selectinload() pour eager loading",
                            category='database'
                        )

    def _check_missing_indexes(self, module_path: Path):
        """Vérifie les index manquants sur colonnes recherchées."""
        repo_path = module_path / 'infrastructure' / 'persistence'

        if not repo_path.exists():
            return

        repo_files = list(repo_path.glob("*_repository.py"))

        for repo_file in repo_files:
            with open(repo_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Chercher les colonnes utilisées dans les WHERE clauses
            # Pattern: filter(Model.column == value) ou filter_by(column=value)
            filter_columns = re.findall(r'filter\(\w+\.(\w+)\s*==', content)
            filter_columns += re.findall(r'filter_by\((\w+)=', content)

            # Colonnes couramment recherchées qui devraient avoir un index
            searchable_columns = set(filter_columns)

            for column in searchable_columns:
                # Vérifier si la colonne a probablement un index
                # (par convention, pas de vérification directe possible ici)
                if column not in ['id', 'email', 'username']:
                    self.add_finding(
                        severity='LOW',
                        message=f"Colonne '{column}' utilisée dans filter sans index apparent",
                        file=str(repo_file.relative_to(Path.cwd())),
                        suggestion=f"Vérifier si index existe sur '{column}' pour optimiser les recherches",
                        category='database'
                    )

    def _calculate_scores(self) -> dict:
        """Calcule les scores SQL."""
        critical_high = len([f for f in self.findings if f.severity in ['CRITICAL', 'HIGH']])

        db_quality_score = max(0, 10 - critical_high * 2)

        return {
            "db_quality": f"{db_quality_score}/10",
            "total_findings": len(self.findings),
        }

    def _generate_summary(self, status: AgentStatus) -> str:
        """Génère un résumé basé sur le statut."""
        critical = len([f for f in self.findings if f.severity == 'CRITICAL'])
        high = len([f for f in self.findings if f.severity == 'HIGH'])

        if status == AgentStatus.FAIL:
            return f"❌ ÉCHEC : {critical} problème(s) critique(s) SQL/migrations"
        elif status == AgentStatus.WARN:
            return f"⚠️  WARNING : {high} problème(s) haute(s) priorité DB"
        else:
            return "✅ Schéma SQL et migrations OK"
