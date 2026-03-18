"""Tests for pod.scopes module."""

from pod.scopes import Scopes


class TestScopes:
    def test_risk_level_known(self):
        assert Scopes.risk_level("catalog.browse") == "low"
        assert Scopes.risk_level("checkout.execute") == "high"
        assert Scopes.risk_level("payment.execute") == "critical"

    def test_risk_level_unknown(self):
        assert Scopes.risk_level("unknown.scope") == "medium"

    def test_is_high_risk(self):
        assert Scopes.is_high_risk("checkout.execute") is True
        assert Scopes.is_high_risk("payment.execute") is True
        assert Scopes.is_high_risk("catalog.browse") is False

    def test_ecommerce_read(self):
        scopes = Scopes.ecommerce_read()
        assert "catalog.browse" in scopes
        assert "checkout.execute" not in scopes

    def test_ecommerce_full(self):
        scopes = Scopes.ecommerce_full()
        assert "catalog.browse" in scopes
        assert "checkout.execute" in scopes
        assert "cart.modify" in scopes

    def test_travel_full(self):
        scopes = Scopes.travel_full()
        assert "availability.search" in scopes
        assert "booking.create" in scopes

    # === Education ===

    def test_education_risk_levels(self):
        assert Scopes.risk_level("course.browse") == "low"
        assert Scopes.risk_level("course.enroll") == "high"
        assert Scopes.risk_level("course.drop") == "high"
        assert Scopes.risk_level("assignment.submit") == "high"
        assert Scopes.risk_level("grades.access") == "medium"
        assert Scopes.risk_level("certificate.request") == "medium"

    def test_education_read(self):
        scopes = Scopes.education_read()
        assert "course.browse" in scopes
        assert "grades.access" in scopes
        assert "course.enroll" not in scopes

    def test_education_full(self):
        scopes = Scopes.education_full()
        assert len(scopes) == 6
        assert "course.browse" in scopes
        assert "course.enroll" in scopes
        assert "assignment.submit" in scopes
        assert "certificate.request" in scopes

    # === Real Estate ===

    def test_realestate_risk_levels(self):
        assert Scopes.risk_level("listing.browse") == "low"
        assert Scopes.risk_level("listing.compare") == "low"
        assert Scopes.risk_level("tour.schedule") == "medium"
        assert Scopes.risk_level("application.submit") == "high"
        assert Scopes.risk_level("lease.sign") == "critical"
        assert Scopes.risk_level("maintenance.request") == "medium"

    def test_realestate_full(self):
        scopes = Scopes.realestate_full()
        assert len(scopes) == 6
        assert "listing.browse" in scopes
        assert "lease.sign" in scopes
        assert "maintenance.request" in scopes

    # === Social Media ===

    def test_social_risk_levels(self):
        assert Scopes.risk_level("content.read") == "low"
        assert Scopes.risk_level("content.create") == "medium"
        assert Scopes.risk_level("content.delete") == "high"
        assert Scopes.risk_level("profile.modify") == "medium"
        assert Scopes.risk_level("messaging.read") == "medium"
        assert Scopes.risk_level("messaging.send") == "high"
        assert Scopes.risk_level("account.settings") == "high"

    def test_social_full(self):
        scopes = Scopes.social_full()
        assert len(scopes) == 7
        assert "content.read" in scopes
        assert "messaging.send" in scopes
        assert "account.settings" in scopes

    # === IoT & Smart Home ===

    def test_iot_risk_levels(self):
        assert Scopes.risk_level("device.read") == "low"
        assert Scopes.risk_level("device.control") == "medium"
        assert Scopes.risk_level("automation.manage") == "high"
        assert Scopes.risk_level("firmware.update") == "high"
        assert Scopes.risk_level("access.grant") == "critical"
        assert Scopes.risk_level("device.remove") == "high"

    def test_iot_full(self):
        scopes = Scopes.iot_full()
        assert len(scopes) == 6
        assert "device.read" in scopes
        assert "access.grant" in scopes
        assert "device.remove" in scopes

    # === Cross-vertical high risk ===

    def test_is_high_risk_new_verticals(self):
        # High risk
        assert Scopes.is_high_risk("course.enroll") is True
        assert Scopes.is_high_risk("application.submit") is True
        assert Scopes.is_high_risk("content.delete") is True
        assert Scopes.is_high_risk("automation.manage") is True
        # Critical risk
        assert Scopes.is_high_risk("lease.sign") is True
        assert Scopes.is_high_risk("access.grant") is True
        # Low/medium risk
        assert Scopes.is_high_risk("course.browse") is False
        assert Scopes.is_high_risk("device.control") is False
        assert Scopes.is_high_risk("content.read") is False
