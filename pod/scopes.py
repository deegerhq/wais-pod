"""
Standard WAIS Scopes by vertical.

Provides a taxonomy of scopes for common website interaction patterns.
Sites and agents use these to agree on what actions are authorized.
"""


class Scopes:
    """Standard WAIS scope definitions."""

    # === E-Commerce ===
    CATALOG_BROWSE = "catalog.browse"
    CATALOG_COMPARE = "catalog.compare"
    CART_MODIFY = "cart.modify"
    CHECKOUT_EXECUTE = "checkout.execute"
    ORDER_TRACK = "order.track"
    RETURN_INITIATE = "return.initiate"
    RETURN_COMPLETE = "return.complete"
    SUBSCRIPTION_MANAGE = "subscription.manage"

    # === Travel & Hospitality ===
    AVAILABILITY_SEARCH = "availability.search"
    BOOKING_CREATE = "booking.create"
    BOOKING_MODIFY = "booking.modify"
    BOOKING_CANCEL = "booking.cancel"
    CLAIM_SUBMIT = "claim.submit"

    # === Financial Services ===
    ACCOUNT_READ = "account.read"
    QUOTE_REQUEST = "quote.request"
    PAYMENT_EXECUTE = "payment.execute"
    DISPUTE_FILE = "dispute.file"
    POLICY_MODIFY = "policy.modify"

    # === Government & Public Services ===
    APPOINTMENT_BOOK = "appointment.book"
    FORM_SUBMIT = "form.submit"
    DOCUMENT_REQUEST = "document.request"
    STATUS_CHECK = "status.check"

    # === Healthcare ===
    APPOINTMENT_SCHEDULE = "appointment.schedule"
    PRESCRIPTION_RENEW = "prescription.renew"
    RECORDS_ACCESS = "records.access"

    # === Education ===
    COURSE_BROWSE = "course.browse"
    COURSE_ENROLL = "course.enroll"
    COURSE_DROP = "course.drop"
    ASSIGNMENT_SUBMIT = "assignment.submit"
    GRADES_ACCESS = "grades.access"
    CERTIFICATE_REQUEST = "certificate.request"

    # === Real Estate ===
    LISTING_BROWSE = "listing.browse"
    LISTING_COMPARE = "listing.compare"
    TOUR_SCHEDULE = "tour.schedule"
    APPLICATION_SUBMIT = "application.submit"
    LEASE_SIGN = "lease.sign"
    MAINTENANCE_REQUEST = "maintenance.request"

    # === Social Media & Content ===
    CONTENT_READ = "content.read"
    CONTENT_CREATE = "content.create"
    CONTENT_DELETE = "content.delete"
    PROFILE_MODIFY = "profile.modify"
    MESSAGING_READ = "messaging.read"
    MESSAGING_SEND = "messaging.send"
    ACCOUNT_SETTINGS = "account.settings"

    # === IoT & Smart Home ===
    DEVICE_READ = "device.read"
    DEVICE_CONTROL = "device.control"
    AUTOMATION_MANAGE = "automation.manage"
    FIRMWARE_UPDATE = "firmware.update"
    ACCESS_GRANT = "access.grant"
    DEVICE_REMOVE = "device.remove"

    # Risk level mappings
    RISK_LEVELS = {
        # E-Commerce
        "catalog.browse": "low",
        "catalog.compare": "low",
        "cart.modify": "medium",
        "checkout.execute": "high",
        "order.track": "low",
        "return.initiate": "medium",
        "return.complete": "high",
        "subscription.manage": "high",
        # Travel
        "availability.search": "low",
        "booking.create": "high",
        "booking.modify": "high",
        "booking.cancel": "high",
        "claim.submit": "medium",
        # Financial
        "account.read": "medium",
        "quote.request": "low",
        "payment.execute": "critical",
        "dispute.file": "medium",
        "policy.modify": "high",
        # Government
        "appointment.book": "medium",
        "form.submit": "high",
        "document.request": "high",
        "status.check": "low",
        # Healthcare
        "appointment.schedule": "medium",
        "prescription.renew": "high",
        "records.access": "critical",
        # Education
        "course.browse": "low",
        "course.enroll": "high",
        "course.drop": "high",
        "assignment.submit": "high",
        "grades.access": "medium",
        "certificate.request": "medium",
        # Real Estate
        "listing.browse": "low",
        "listing.compare": "low",
        "tour.schedule": "medium",
        "application.submit": "high",
        "lease.sign": "critical",
        "maintenance.request": "medium",
        # Social Media & Content
        "content.read": "low",
        "content.create": "medium",
        "content.delete": "high",
        "profile.modify": "medium",
        "messaging.read": "medium",
        "messaging.send": "high",
        "account.settings": "high",
        # IoT & Smart Home
        "device.read": "low",
        "device.control": "medium",
        "automation.manage": "high",
        "firmware.update": "high",
        "access.grant": "critical",
        "device.remove": "high",
    }

    @classmethod
    def risk_level(cls, scope: str) -> str:
        """Get the default risk level for a scope."""
        return cls.RISK_LEVELS.get(scope, "medium")

    @classmethod
    def is_high_risk(cls, scope: str) -> bool:
        """Check if a scope is high or critical risk."""
        return cls.risk_level(scope) in ("high", "critical")

    @classmethod
    def ecommerce_read(cls) -> list[str]:
        """Common read-only e-commerce scopes."""
        return [cls.CATALOG_BROWSE, cls.CATALOG_COMPARE, cls.ORDER_TRACK]

    @classmethod
    def ecommerce_full(cls) -> list[str]:
        """Full e-commerce scopes including transactions."""
        return [
            cls.CATALOG_BROWSE, cls.CATALOG_COMPARE, cls.CART_MODIFY,
            cls.CHECKOUT_EXECUTE, cls.ORDER_TRACK,
            cls.RETURN_INITIATE, cls.RETURN_COMPLETE,
        ]

    @classmethod
    def travel_full(cls) -> list[str]:
        """Full travel scopes."""
        return [
            cls.AVAILABILITY_SEARCH, cls.BOOKING_CREATE,
            cls.BOOKING_MODIFY, cls.BOOKING_CANCEL, cls.CLAIM_SUBMIT,
        ]

    @classmethod
    def education_read(cls) -> list[str]:
        """Read-only education scopes."""
        return [cls.COURSE_BROWSE, cls.GRADES_ACCESS]

    @classmethod
    def education_full(cls) -> list[str]:
        """Full education scopes."""
        return [
            cls.COURSE_BROWSE, cls.COURSE_ENROLL, cls.COURSE_DROP,
            cls.ASSIGNMENT_SUBMIT, cls.GRADES_ACCESS, cls.CERTIFICATE_REQUEST,
        ]

    @classmethod
    def realestate_full(cls) -> list[str]:
        """Full real estate scopes."""
        return [
            cls.LISTING_BROWSE, cls.LISTING_COMPARE, cls.TOUR_SCHEDULE,
            cls.APPLICATION_SUBMIT, cls.LEASE_SIGN, cls.MAINTENANCE_REQUEST,
        ]

    @classmethod
    def social_full(cls) -> list[str]:
        """Full social media scopes."""
        return [
            cls.CONTENT_READ, cls.CONTENT_CREATE, cls.CONTENT_DELETE,
            cls.PROFILE_MODIFY, cls.MESSAGING_READ, cls.MESSAGING_SEND,
            cls.ACCOUNT_SETTINGS,
        ]

    @classmethod
    def iot_full(cls) -> list[str]:
        """Full IoT & smart home scopes."""
        return [
            cls.DEVICE_READ, cls.DEVICE_CONTROL, cls.AUTOMATION_MANAGE,
            cls.FIRMWARE_UPDATE, cls.ACCESS_GRANT, cls.DEVICE_REMOVE,
        ]
