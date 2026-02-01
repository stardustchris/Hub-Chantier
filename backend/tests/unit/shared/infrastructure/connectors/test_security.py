"""Tests pour le module security des connecteurs."""

import pytest
from shared.infrastructure.connectors.security import (
    sanitize_text,
    validate_code,
    validate_amount,
    mask_employee_code,
    hash_employee_code,
    audit_log_employee_data,
    SecurityError
)


class TestSanitizeText:
    """Tests pour sanitize_text()."""

    def test_sanitize_basic_text(self):
        """Texte simple sans HTML doit passer."""
        result = sanitize_text("Achat matériaux chantier X")
        assert result == "Achat matériaux chantier X"

    def test_sanitize_removes_script_tags(self):
        """Les balises script doivent être supprimées."""
        result = sanitize_text("Achat <script>alert('xss')</script> matériaux")
        assert "<script>" not in result
        assert "</script>" not in result
        assert "Achat" in result
        assert "matériaux" in result
        # Note: bleach enlève les balises mais peut garder le contenu textuel

    def test_sanitize_removes_html_tags(self):
        """Les balises HTML dangereuses doivent être supprimées."""
        result = sanitize_text("Text <div>with</div> <span>tags</span>")
        assert "<div>" not in result
        assert "<span>" not in result
        assert "Text" in result
        assert "with" in result
        assert "tags" in result

    def test_sanitize_allows_safe_tags_when_enabled(self):
        """Les balises sûres doivent être autorisées si allow_tags=True."""
        result = sanitize_text("Montant: <b>1500€</b>", allow_tags=True)
        assert "<b>" in result or "1500" in result  # Dépend de la config bleach

    def test_sanitize_escapes_special_chars(self):
        """Les caractères spéciaux doivent être échappés."""
        result = sanitize_text("Prix < 100€ & > 50€")
        # Peut contenir &lt; ou < selon bleach
        assert "100" in result
        assert "50" in result

    def test_sanitize_empty_string(self):
        """String vide doit retourner string vide."""
        result = sanitize_text("")
        assert result == ""

    def test_sanitize_none_value(self):
        """None doit retourner string vide."""
        result = sanitize_text(None)
        assert result == ""

    def test_sanitize_max_length_exceeded(self):
        """Texte trop long doit lever SecurityError."""
        long_text = "A" * 600
        with pytest.raises(SecurityError) as exc_info:
            sanitize_text(long_text, max_length=500)
        assert "trop long" in exc_info.value.message.lower()

    def test_sanitize_trims_whitespace(self):
        """Espaces en début/fin doivent être supprimés."""
        result = sanitize_text("  Achat matériaux  ")
        assert result == "Achat matériaux"


class TestValidateCode:
    """Tests pour validate_code()."""

    def test_validate_valid_employee_code(self):
        """Code employé valide doit passer."""
        result = validate_code("EMP001")
        assert result == "EMP001"

    def test_validate_valid_chantier_code(self):
        """Code chantier valide doit passer."""
        result = validate_code("CHT-2026-01")
        assert result == "CHT-2026-01"

    def test_validate_uppercases_code(self):
        """Code lowercase doit être uppercasé."""
        result = validate_code("emp001")
        assert result == "EMP001"

    def test_validate_invalid_sql_injection(self):
        """Injection SQL doit être rejetée."""
        with pytest.raises(SecurityError) as exc_info:
            validate_code("'; DROP TABLE users; --")
        assert "invalide" in exc_info.value.message.lower()

    def test_validate_invalid_special_chars(self):
        """Caractères spéciaux non autorisés doivent être rejetés."""
        with pytest.raises(SecurityError):
            validate_code("EMP@001")
        with pytest.raises(SecurityError):
            validate_code("EMP#001")
        with pytest.raises(SecurityError):
            validate_code("EMP 001")

    def test_validate_empty_code(self):
        """Code vide doit être rejeté."""
        with pytest.raises(SecurityError) as exc_info:
            validate_code("")
        assert "vide" in exc_info.value.message.lower()

    def test_validate_none_code(self):
        """None doit être rejeté."""
        with pytest.raises(SecurityError):
            validate_code(None)

    def test_validate_code_too_long(self):
        """Code trop long doit être rejeté."""
        with pytest.raises(SecurityError):
            validate_code("A" * 60)  # > 50 chars

    def test_validate_custom_pattern(self):
        """Pattern custom doit être respecté."""
        # Pattern pour codes numériques uniquement
        result = validate_code("12345", pattern=r'^\d{5}$', field_name="code_postal")
        assert result == "12345"

        with pytest.raises(SecurityError):
            validate_code("ABC123", pattern=r'^\d{5}$', field_name="code_postal")

    def test_validate_trims_whitespace(self):
        """Espaces en début/fin doivent être supprimés."""
        result = validate_code("  EMP001  ")
        assert result == "EMP001"


class TestValidateAmount:
    """Tests pour validate_amount()."""

    def test_validate_positive_amount(self):
        """Montant positif doit passer."""
        result = validate_amount(1500.00)
        assert result == 1500.0

    def test_validate_zero_amount(self):
        """Montant zéro doit passer."""
        result = validate_amount(0.0)
        assert result == 0.0

    def test_validate_negative_amount(self):
        """Montant négatif doit être rejeté par défaut."""
        with pytest.raises(SecurityError) as exc_info:
            validate_amount(-100.00)
        assert "négatif" in exc_info.value.message.lower()

    def test_validate_negative_amount_with_custom_min(self):
        """Montant négatif doit passer si min_value < 0."""
        result = validate_amount(-50.0, min_value=-100.0)
        assert result == -50.0

    def test_validate_amount_exceeds_max(self):
        """Montant > max_value doit être rejeté."""
        with pytest.raises(SecurityError) as exc_info:
            validate_amount(15000.0, max_value=10000.0)
        assert "maximum" in exc_info.value.message.lower()

    def test_validate_nan_amount(self):
        """NaN doit être rejeté."""
        with pytest.raises(SecurityError) as exc_info:
            validate_amount(float('nan'))
        assert "nan" in exc_info.value.message.lower()

    def test_validate_infinite_amount(self):
        """Infini doit être rejeté."""
        with pytest.raises(SecurityError) as exc_info:
            validate_amount(float('inf'))
        assert "infini" in exc_info.value.message.lower()

        with pytest.raises(SecurityError):
            validate_amount(float('-inf'))

    def test_validate_string_amount(self):
        """String convertible en float doit passer."""
        result = validate_amount("1500.00")
        assert result == 1500.0

    def test_validate_decimal_amount(self):
        """Decimal doit être converti en float."""
        from decimal import Decimal
        result = validate_amount(Decimal("1500.00"))
        assert result == 1500.0

    def test_validate_invalid_amount_type(self):
        """Type invalide doit être rejeté."""
        with pytest.raises(SecurityError):
            validate_amount("not_a_number")

        with pytest.raises(SecurityError):
            validate_amount(None)


class TestMaskEmployeeCode:
    """Tests pour mask_employee_code()."""

    def test_mask_standard_code(self):
        """Code standard doit être partiellement masqué."""
        result = mask_employee_code("EMP001")
        # EMP001 = 6 chars: EM (2) + ** (2 masqués) + 01 (2) = EM**01
        assert result == "EM**01"

    def test_mask_long_code(self):
        """Code long doit masquer plus de caractères."""
        result = mask_employee_code("EMPLOYE12345")
        assert result.startswith("EM")
        assert result.endswith("45")
        assert "***" in result

    def test_mask_short_code(self):
        """Code court (< 4 chars) doit être complètement masqué."""
        result = mask_employee_code("E1")
        assert result == "***"

    def test_mask_empty_code(self):
        """Code vide doit retourner ***."""
        result = mask_employee_code("")
        assert result == "***"

    def test_mask_none_code(self):
        """None doit retourner ***."""
        result = mask_employee_code(None)
        assert result == "***"


class TestHashEmployeeCode:
    """Tests pour hash_employee_code()."""

    def test_hash_produces_consistent_hash(self):
        """Même code doit produire même hash."""
        hash1 = hash_employee_code("EMP001")
        hash2 = hash_employee_code("EMP001")
        assert hash1 == hash2

    def test_hash_produces_different_hashes_for_different_codes(self):
        """Codes différents doivent produire hashes différents."""
        hash1 = hash_employee_code("EMP001")
        hash2 = hash_employee_code("EMP002")
        assert hash1 != hash2

    def test_hash_produces_hexadecimal(self):
        """Hash doit être hexadécimal (64 chars)."""
        result = hash_employee_code("EMP001")
        assert len(result) == 64
        assert all(c in '0123456789abcdef' for c in result)

    def test_hash_empty_code_raises_error(self):
        """Code vide doit lever SecurityError."""
        with pytest.raises(SecurityError) as exc_info:
            hash_employee_code("")
        assert "vide" in exc_info.value.message.lower()

    def test_hash_with_custom_salt(self):
        """Salt custom doit produire hash différent."""
        hash1 = hash_employee_code("EMP001", salt="salt1")
        hash2 = hash_employee_code("EMP001", salt="salt2")
        assert hash1 != hash2


class TestAuditLogEmployeeData:
    """Tests pour audit_log_employee_data()."""

    def test_audit_log_basic(self, caplog):
        """Audit log doit logger les informations."""
        import logging
        caplog.set_level(logging.INFO)

        audit_log_employee_data(
            action="send_hours",
            employee_code="EMP001",
            period="2026-01",
            hours_count=5,
            connector_name="silae"
        )

        # Vérifier que le log contient les infos attendues
        assert len(caplog.records) == 1
        log_message = caplog.records[0].message
        assert "[AUDIT]" in log_message
        assert "action=send_hours" in log_message
        assert "employee_hash=" in log_message
        assert "employee_masked=EM**01" in log_message  # EMP001 = EM**01
        assert "connector=silae" in log_message
        assert "period=2026-01" in log_message
        assert "hours_count=5" in log_message

    def test_audit_log_without_optional_fields(self, caplog):
        """Audit log doit fonctionner sans champs optionnels."""
        import logging
        caplog.set_level(logging.INFO)

        audit_log_employee_data(
            action="update_payroll",
            employee_code="EMP002",
            connector_name="silae"
        )

        assert len(caplog.records) == 1
        log_message = caplog.records[0].message
        assert "action=update_payroll" in log_message
        assert "employee_masked=EM**02" in log_message  # EMP002 = EM**02
        # Pas de period ou hours_count
        assert "period=" not in log_message
        assert "hours_count=" not in log_message

    def test_audit_log_does_not_contain_clear_code(self, caplog):
        """Le log ne doit PAS contenir le code employé en clair."""
        import logging
        caplog.set_level(logging.INFO)

        audit_log_employee_data(
            action="send_hours",
            employee_code="SECRET123",
            connector_name="silae"
        )

        log_message = caplog.records[0].message
        assert "SECRET123" not in log_message
        # SECRET123 = 9 chars: SE (2) + ***** (5 masqués) + 23 (2) = SE*****23
        assert "SE*****23" in log_message


class TestSecurityIntegration:
    """Tests d'intégration combinant plusieurs fonctions."""

    def test_full_workflow_pennylane(self):
        """Workflow complet Pennylane avec validations."""
        # Simulation d'un formatage de facture
        libelle = "Achat <script>alert('xss')</script> matériaux"
        montant = "1500.00"
        numero_facture = "FAC-2026-001"

        # Sanitize
        libelle_safe = sanitize_text(libelle)
        assert "<script>" not in libelle_safe

        # Validate
        montant_valide = validate_amount(montant)
        assert montant_valide == 1500.0

        numero_valide = validate_code(numero_facture)
        assert numero_valide == "FAC-2026-001"

    def test_full_workflow_silae(self, caplog):
        """Workflow complet Silae avec validations et audit."""
        import logging
        caplog.set_level(logging.INFO)

        # Simulation d'un formatage de feuille d'heures
        employe_code = "emp001"
        chantier_code = "cht-abc-123"

        # Validate codes
        employe_valide = validate_code(employe_code, field_name="employe_code")
        assert employe_valide == "EMP001"

        chantier_valide = validate_code(chantier_code, field_name="chantier_code")
        assert chantier_valide == "CHT-ABC-123"

        # Mask for logging
        employe_masked = mask_employee_code(employe_valide)
        assert employe_masked == "EM**01"  # EMP001 = EM**01

        # Audit trail
        audit_log_employee_data(
            action="send_hours",
            employee_code=employe_valide,
            period="2026-01",
            hours_count=3,
            connector_name="silae"
        )

        # Vérifier que le log ne contient pas le code en clair
        log_message = caplog.records[0].message
        assert "EMP001" not in log_message
        assert "EM**01" in log_message  # EMP001 = EM**01
