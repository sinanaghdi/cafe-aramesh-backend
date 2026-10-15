from backend.app.core.config import settings

WAITER_PIN = settings.waiter_pin
CONFIRMATION_TTL_MINUTES = max(1, settings.confirmation_ttl_minutes)
